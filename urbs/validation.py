import pandas as pd


def validate_input(data):
    """ Input validation function

    This function raises errors if inconsistent or illogical inputs are
    made, that might lead to erreneous results.

    Args:
        data: Input data frames as read in by input.read_excel

    Returns:
        Customized error messages.

    """

    # Ensure correct formation of vertex rule
    for (stf, sit, pro) in data['process'].index:
        for com in data['commodity'].index.get_level_values('Commodity'):
            simplified_pro_com_index = ([(st, p, c) for st, p, c, d in
                                        data['process_commodity'].index
                                        .tolist()])
            simplified_com_index = ([(st, s, c) for st, s, c, t in
                                    data['commodity'].index.tolist()])
            if ((stf, pro, com) in simplified_pro_com_index and
                (stf, sit, com) not in simplified_com_index):
                raise ValueError('Commodities used in a process at a site must'
                                 ' be specified in the commodity input sheet'
                                 '! The tuple (' + stf + ',' + sit + ',' + com
                                 + ') is not in commodity input sheet.')
