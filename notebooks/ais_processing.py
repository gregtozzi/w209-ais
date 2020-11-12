import csv
import json
import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString


def ais_to_json(ais_path, json_path):
    """
    Given a CSV file in the format used by marinecadestre.gov
    return a JSON file wherein each unique MMSI contains
    elements necessary later to build a Pandas dataframe. No
    real processing is done on the values at this stage.
    
    Args:
        ais_path:  A str giving the path to the input file
        json_path: A str giving the path to the output file
        
    Returns:
        None
    """
    # Scan the file once, extracting unique MMSIs
    MMSIs = set()
    with open(ais_path) as aisfile:
        reader = csv.reader(aisfile)
        next(reader) # Cut the header
        for row in reader:
            MMSIs.add(row[0])

    aisfile.close()
    
    # Build a dict to house the data
    vessels = {}
    for MMSI in MMSIs:
        vessels[MMSI] = {'LAT': [],
                         'LON': [],
                         'DTG': [],
                         'COG': [],
                         'SOG': [],
                         'Name': '',
                         'Type': '',
                         'LOA'  : 0,
                         'Beam' : 0,
                         'Draft': 0}

    
    # Scan the file again, adding values to the dict
    with open(ais_path) as aisfile:
        reader = csv.reader(aisfile)
        next(reader) # Cut the header
        for row in reader:
            vessels[row[0]]['DTG'].append(row[1])
            vessels[row[0]]['LAT'].append(row[2])
            vessels[row[0]]['LON'].append(row[3])
            vessels[row[0]]['SOG'].append(row[4])
            vessels[row[0]]['COG'].append(row[5])
            vessels[row[0]]['Name']  = row[7]
            vessels[row[0]]['Type']  = row[10]
            vessels[row[0]]['LOA']   = row[12]
            vessels[row[0]]['Beam']  = row[13]
            vessels[row[0]]['Draft'] = row[14]
        
    # Save the JSON file
    with open(json_path, 'w') as jsonfile:
        json.dump(vessels, jsonfile)



def analyze_vessel_json(json_path, Prune=False, prune_path=None):
    """
    Given a JSON file structured as the output of
    ais_to_json, report some basic statistics.  Can
    be used to create a pruned file that removes
    non-moving vessels (defined as vessels whose max
    speed is under 2 kt) and vessels that do not have
    at least 10 reports.

    Args:
        json_path:  A str giving the path to the JSON file
        Prune:      Bool
        prine_path: str giving path to output file (if pruning)
        
    Returns:
        None
    """
    # Load the JSON
    with open(json_path, 'r') as aisfile:
        data = json.load(aisfile)

    # How many vessels do we have?
    num_vessels = len(data)

    # Set up arrays to store statistics
    never_move     = []
    few_reports    = []
    num_reports    = np.array([])
    moving_reports = np.array([])
    max_speed      = np.array([])

    # Compute values of interest
    for MMSI in data.keys():
        vsl = data[MMSI]
        SOG = np.array(vsl['SOG']).astype('float')
        if SOG.max() < 2:
            never_move.append(MMSI)
        if len(SOG) < 10:
            few_reports.append(MMSI)
        num_reports    = np.append(num_reports, len(SOG))
        moving_reports = np.append(moving_reports, (SOG > 2).sum())
        max_speed      = np.append(max_speed, SOG.max())

    print('---------AIS Data Report---------\n')
    print('Total vessels - {}\n'.format(num_vessels))
    print('Vessels that never exceed 2kt - {}\n'.format(len(never_move)))
    print('------------------\n')
    print('Reports per vessel\n')
    print('------------------\n')
    print('Mean   - {}\n'.format(num_reports.mean()))
    print('Median - {}\n'.format(np.median(num_reports)))
    print('Max    - {}\n'.format(num_reports.max()))
    print('-------------------------\n')
    print('Moving reports per vessel\n')
    print('-------------------------\n')
    print('Mean   - {}\n'.format(moving_reports.mean()))
    print('Median - {}\n'.format(np.median(moving_reports)))
    print('Max    - {}\n'.format(moving_reports.max()))
    print('--------------------\n')
    print('Max speed per vessel\n')
    print('--------------------\n')
    print('Mean   - {}\n'.format(max_speed.mean()))
    print('Median - {}\n'.format(np.median(max_speed)))
    print('Max    - {}\n'.format(max_speed.max()))

    if Prune:
        cut_MMSI = set(never_move).union(set(few_reports))
        for MMSI in cut_MMSI:
            data.pop(MMSI)
        with open(prune_path, 'w') as jsonfile:
            json.dump(data, jsonfile)


def pandize_data(json_path):
    """
    Given a JSON file structured as the ouput of
    ais_to_json and possibly pruned with
    analyze_vessel_json, convert certain elements
    of the data to pandas dataframes.  This is the
    first function in this module that actually
    returns data.

    Args:
        json_path: A str giving the path to the output file
        
    Returns:
        A dict of pandas dataframes and associated meta-
        data for each vessel in the input file.
    """
    with open(json_path, 'r') as aisfile:
        data = json.load(aisfile)

    df_col = ['LAT', 'LON', 'COG', 'SOG']

    for MMSI in data.keys():
        df = pd.DataFrame({'DTG': data[MMSI]['DTG']})
        data[MMSI].pop('DTG')
        for col in df_col:
            df[col] = data[MMSI][col]
            data[MMSI].pop(col)
        df['DTG'] = pd.to_datetime(df['DTG'])
        df['LAT'] = pd.to_numeric(df['LAT'])
        df['LON'] = pd.to_numeric(df['LON'])
        df['COG'] = pd.to_numeric(df['COG'])
        df['SOG'] = pd.to_numeric(df['SOG'])
        df.sort_values('DTG', inplace=True, ignore_index=True)
        df['geometry'] = [Point(xy) for xy in zip(df['LON'], df['LAT'])]
        data[MMSI]['df'] = df

    return(data)


def detect_transits(df):
    """
    Given a dataframe structured as the output
    of pandize_data, identify discrete vessel
    transits.

    Args:
        df: pd.DataFrame structured as the output
            of pandize_data
        
    Returns: A list of pd.DataFrames for each
             detected transit
        
    """
    # Detect large changes in time between reports
    time_chunks = []
    time_delta  = np.where(df.DTG.diff() > np.timedelta64(1,'h'))[0]
    time_delta  = np.insert(time_delta, 0, 0)
    time_delta  = np.append(time_delta, df.shape[0])
    time_delta_left  = time_delta[:-1]
    time_delta_right = time_delta[1:]
    for i, j in zip(time_delta_left, time_delta_right):
        time_chunks.append(df[i:j])

    # Detect long duration stops
    transits = []
    for chunk in time_chunks:
        transition       = np.array(chunk.SOG.rolling(5).max() < 0.5)
        transition_index = (np.where(transition[:-1] != transition[1:])[0])
        transition_index = np.insert(transition_index, 0, 0)
        transition_index = np.append(transition_index, len(df.SOG))
        transition_left  = transition_index[:-1]
        transition_right = transition_index[1:]
        for i, j in zip(transition_left, transition_right):
            transits.append(chunk[i:j])
    vsl_transits = [transit for transit in transits if (transit.SOG.mean() > 0.5) & (len(transit.SOG) > 5)]
    return vsl_transits


def collapse_transits(vsl_dict):
    """
    Given a dict structured as an entry of the output
    of pandize_data, apply detect_transits to
    divide the pd.DataFrame into discrete transits,
    zip those transits into single lines of a new
    pd.DataFrame with attached metadata.

    Args:
        vsl_dict: dict structured as an entry of
                  the output of pandize_data
        
    Returns: A list of pd.DataFrames for each
             detected transit
        
    """
    days      = {0: 'Mon',
                 1: 'Tue',
                 2: 'Wed',
                 3: 'Thu',
                 4: 'Fri',
                 5: 'Sat',
                 6: 'Sun'}

    months    = {1: 'Jan',
                 2: 'Feb',
                 3: 'Mar',
                 4: 'Apr',
                 5: 'May',
                 6: 'Jun',
                 7: 'Jul',
                 8: 'Aug',
                 9: 'Sep',
                 10: 'Oct',
                 11: 'Nov',
                 12: 'Dec'}

    transits  = detect_transits(vsl_dict['df'])

    if len(transits) > 0:
        geometry  = [LineString(list(transit.geometry)) for transit in transits]
        max_SOG   = [transit.SOG.max() for transit in transits]
        start_DTG = [transit.DTG.min() - np.timedelta64(7, 'h') for transit in transits]
        end_DTG   = [transit.DTG.max() - np.timedelta64(7, 'h') for transit in transits]
        if vsl_dict['LOA'] == '':
            LOA   = [0 for i in range(len(max_SOG))]
        else:
            LOA   = [float(vsl_dict['LOA']) for i in range(len(max_SOG))]
        vsl_data  = {'start_DTG': start_DTG,
                     'end_DTG': end_DTG,
                     'SOG': max_SOG,
                     'LOA_unbinned': LOA,
                     'geometry': geometry}

        df          = pd.DataFrame.from_dict(vsl_data)
        day         = df.start_DTG.dt.dayofweek
        day         = [days[i] for i in day]
        df['day']   = day
        month       = df.start_DTG.dt.month
        month       = [months[i] for i in month]
        df['month'] = month

        return df

    else: return []


def transits_df(vsl_dict, output_path=None):
    """
    Given a dict of the structure returned by
    pandize_data, return a single pd.DataFrame
    suitable for use as input to the visualization.

    Args:
        vsl_dict: dict structured as an entry of
                  the output of pandize_data
        output_path: str giving the path of the
                     output file, if saving the
                     output is desired

    Returns:
        A pd.DataFrame that can be used as input to
        the visualization
    """
    MMSIs = list(vsl_dict.keys())
    all_transits = [collapse_transits(vsl_dict[MMSI]) for MMSI in MMSIs]
    all_transits = [transit for transit in all_transits if (type(transit) != list)]
    df = pd.concat(all_transits)
    df.reset_index()

    # Add transit lengths (not in usable dimensions,
    # though this is probably fixable).
    length = [x.length for x in df.geometry]
    df['length'] = length

    # Add binned values of vessel max speeds
    df['max_SOG'] = (np.floor(df['SOG'] / 10) * 10).astype(int).astype(str) + '-' + (np.floor(df['SOG'] / 10 + 1) * 10).astype(int).astype(str) + 'kt'

    # Add binned values of vessel lengths
    df['LOA'] = (np.floor(df['LOA_unbinned'] / 100) * 100).astype(int).astype(str) + '-' + (np.floor(df['LOA_unbinned'] / 100 + 1) * 100).astype(int).astype(str) + 'm'
    df = df.sort_values('length', ascending=False).reset_index(drop=True)
    # Return and (maybe) write the output
    if output_path:
        df.to_csv(output_path, index=False)
    return df


def binned_transits(df, output_path=None):
    """
    Given a pd.DataFrame structured as the output of
    transits_df, bin along several measures and combine
    LineStrings into MultiLineStrings.  The intent it
    to stuff more data into the visualization by
    working around Altair's 5,000 line limitation.  This
    might not be necessary if I was working directly
    in Vega-Lite.  Something to explore...

    Args:
        df: pd.DataFrame structured as the output of
            transits_df

    """
    LOA      = []
    max_SOG  = []
    geometry = []

    for i in df.LOA.unique():
        for j in df.max_SOG.unique():
            geo_list = df.geometry[(df.LOA == i) & (df.max_SOG == j)].to_list()
            if len(geo_list) > 0:
                LOA.append(i)
                max_SOG.append(j)
                geometry.append(MultiLineString(geo_list))

    data_dict = {'LOA': LOA,
                 'max_SOG': max_SOG,
                 'geometry': geometry}

    df_out = pd.DataFrame.from_dict(data_dict)

    if output_path:
        df_out.to_csv(output_path)

    return df_out


def cluster_transits(df, diff_threshold=0.01, hausdorff_threshold=0.03):
    lines = df.geometry
    # Compute a bounding box for each transit
    c_vec = np.array([np.array(x.bounds) for x in df.geometry])

    clusters = []
    index_stack = np.arange(len(df))
    while len(index_stack) > 1:
        cluster = []
        i = index_stack[0]
        cluster.append(i)
        c_vec_i = c_vec[i]
        index_stack = index_stack[1:]
        c_vec_j = c_vec[index_stack]
        abs_diff = (np.abs(c_vec_j - c_vec_i)).max(axis=1)
        candidates = index_stack[np.where(abs_diff < diff_threshold)[0]]
        h_dist = np.array([lines[i].hausdorff_distance(lines[j]) for j in candidates])
        cluster_mbrs = candidates[np.where(h_dist < hausdorff_threshold)[0]]
        for mbr in cluster_mbrs:
            cluster.append(mbr)
        clusters.append(cluster)
        index_stack = np.setdiff1d(index_stack, cluster_mbrs)
    return clusters







