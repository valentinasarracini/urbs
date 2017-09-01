import pandas as pd
from xlrd import XLRDError


def read_intertemporal(folder):
    glob_input = os.path.join(folder, '*.xlsx')
    result_files = sorted(glob.glob(glob_input))
    return input_files


def read_excel(input_files):
    """Read Excel input file and prepare URBS input dict.

    Reads an Excel spreadsheet that adheres to the structure shown in
    mimo-example.xlsx. Two preprocessing steps happen here:
    1. Column titles in 'Demand' and 'SupIm' are split, so that
    'Site.Commodity' becomes the MultiIndex column ('Site', 'Commodity').
    2. The attribute 'annuity-factor' is derived here from the columns 'wacc'
    and 'depreciation' for 'Process', 'Transmission' and 'Storage'.

    Args:
        filename: filename to an Excel spreadsheet with the required sheets
            'Commodity', 'Process', 'Transmission', 'Storage', 'Demand' and
            'SupIm'.

    Returns:
        a dict of 6 DataFrames

    Example:
        >>> data = read_excel('mimo-example.xlsx')
        >>> data['global'].loc['CO2 limit', 'value']
        150000000
    """
    
    gl = []
    sit = []
    com = []
    pro = []
    pro_com = []
    tra = []
    sto = []
    dem = []
    sup = []
    bsp = []
    ds = []
    
    for filename in files:
        with pd.ExcelFile(filename) as xls:
            glob = xls.parse('Global').set_index(['Property'])
            year = glob.loc['Year']['value']
            glob = glob.drop(['Year']).drop(['description'], axis=1)
            
            glob = pd.concat([glob], keys=[year], names=['year'])
            gl.append(glob)
            site = xls.parse('Site').set_index(['Name'])
            site = pd.concat([site], keys=[year], names=['year'])
            sit.append(site)
            commodity = (
                xls.parse('Commodity').set_index(['Site', 'Commodity', 'Type']))
            commodity = pd.concat([commodity], keys=[year], names=['year'])
            com.append(commodity)
            process = xls.parse('Process').set_index(['Site', 'Process'])
            process = pd.concat([process], keys=[year], names=['year'])
            pro.append(process)
            process_commodity = (
                xls.parse('Process-Commodity')
                   .set_index(['Process', 'Commodity', 'Direction']))
            process_commodity = pd.concat([process_commodity], keys=[year], names=['year'])
            pro_com.append(process_commodity)
            transmission = (
                xls.parse('Transmission')
                   .set_index(['Site In', 'Site Out',
                           'Transmission', 'Commodity']))
            transmission = pd.concat([transmission], keys=[year], names=['year'])
            tra.append(transmission)
            storage = (
                xls.parse('Storage').set_index(['Site', 'Storage', 'Commodity']))
            storage = pd.concat([storage], keys=[year], names=['year'])
            sto.append(storage)
            demand = xls.parse('Demand').set_index(['t'])
            demand = pd.concat([demand], keys=[year], names=['year'])
            dem.append(demand)
            supim = xls.parse('SupIm').set_index(['t'])
            supim = pd.concat([supim], keys=[year], names=['year'])
            sup.append(supim)
            buy_sell_price = xls.parse('Buy-Sell-Price').set_index(['t'])
            buy_sell_price = pd.concat([buy_sell_price], keys=[year], names=['year'])
            bsp.append(buy_sell_price)
            dsm = xls.parse('DSM').set_index(['Site', 'Commodity'])
            dsm = pd.concat([dsm], keys=[year], names=['year'])
            ds.append(dsm)

        # prepare input data
        # split columns by dots '.', so that 'DE.Elec' becomes the two-level
        # column index ('DE', 'Elec')
        demand.columns = split_columns(demand.columns, '.')
        supim.columns = split_columns(supim.columns, '.')
        buy_sell_price.columns = split_columns(buy_sell_price.columns, '.')
        
    data = {
        'global': pd.concat(gl),
        'site': pd.concat(sit),
        'commodity': pd.concat(com),
        'process': pd.concat(pro),
        'process_commodity': pd.concat(pro_com),
        'transmission': pd.concat(tra),
        'storage': pd.concat(sto),
        'demand': pd.concat(dem),
        'supim': pd.concat(sup),
        'buy_sell_price': pd.concat(bsp),
        'dsm': pd.concat(ds)
        }

        # sort nested indexes to make direct assignments work
    for key in data:
        if isinstance(data[key].index, pd.core.index.MultiIndex):
            data[key].sortlevel(inplace=True)
    return data


def split_columns(columns, sep='.'):
    """Split columns by separator into MultiIndex.

    Given a list of column labels containing a separator string (default: '.'),
    derive a MulitIndex that is split at the separator string.

    Args:
        columns: list of column labels, containing the separator string
        sep: the separator string (default: '.')

    Returns:
        a MultiIndex corresponding to input, with levels split at separator

    Example:
        >>> split_columns(['DE.Elec', 'MA.Elec', 'NO.Wind'])
        MultiIndex(levels=[['DE', 'MA', 'NO'], ['Elec', 'Wind']],
                   labels=[[0, 1, 2], [0, 0, 1]])

    """
    if len(columns) == 0:
        return columns
    column_tuples = [tuple(col.split('.')) for col in columns]
    return pd.MultiIndex.from_tuples(column_tuples)


def get_input(prob, name):
    """Return input DataFrame of given name from urbs instance.

    These are identical to the key names returned by function `read_excel`.
    That means they are lower-case names and use underscores for word
    separation, e.g. 'process_commodity'.

    Args:
        prob: a urbs model instance
        name: an input DataFrame name ('commodity', 'process', ...)

    Returns:
        the corresponding input DataFrame

    """
    if hasattr(prob, name):
        # classic case: input data DataFrames are accessible via named
        # attributes, e.g. `prob.process`.
        return getattr(prob, name)
    elif hasattr(prob, '_data') and name in prob._data:
        # load case: input data is accessible via the input data cache dict
        return prob._data[name]
    else:
        # unknown
        raise ValueError("Unknown input DataFrame name!")
