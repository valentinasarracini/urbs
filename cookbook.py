import os
import pyomo.environ
import shutil
import numpy as np
import urbs
from datetime import datetime
from pyomo.opt.base import SolverFactory

# SCENARIO GENERATORS

# Commodity prices

def scen_co2price(site, co2price):
    # site = string; Site where the value should be changed.
    # value = float; New set value

    def scenario(data):
        data['commodity'].loc[(site, 'CO2', 'Env'), 'price'] = co2price
        return data

    scenario.__name__ = 'scenario_CO2-price-' + '{:04}'.format(value)
    # used for result filenames
    return scenario


def scen_gasprice(site, gasprice):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['commodity'].loc[(site, 'Gas', 'Stock'), 'price'] = gasprice
        return data

    scenario.__name__ = 'scenario_Gas-price-' + '{:04}'.format(value)
    # used for result filenames
    return scenario


def scen_elecprice(site, elecprice):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['commodity'].loc[(site, 'Gridelec', 'Stock'), 'price'] = elecprice
        return data

    scenario.__name__ = 'scenario_Elec-price-' + '{:04}'.format(value)
    # used for result filenames
    return scenario


def scen_geothprice(site, geothprice):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['commodity'].loc[(site, 'Geothermal', 'Stock'), 'price'] = (
                geothprice)
        return data

    scenario.__name__ = 'scenario_GT-price-' + '{:04}'.format(value)
    # used for result filenames
    return scenario


# Process commodities

def scen_chpprop(process, Eleceff):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['process_commodity'].loc[(process, 'Elec', 'Out'), 'ratio'] = (
                Eleceff)
        data['process_commodity'].loc[(process, 'HeatHigh', 'Out'), 'ratio'] = (
                1 - 1.5 * Eleceff)
        return data

    scenario.__name__ = 'scenario_CHP-elec-' + '{:04.4f}'.format(value)
    # used for result filenames
    return scenario


# Global quantities

def scen_wacc(value):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['process'].loc[:, 'wacc'] = value
        data['transmission'].loc[:, 'wacc'] = value
        data['storage'].loc[:, 'wacc'] = value
        return data

    scenario.__name__ = 'scenario_wacc-' + '{:03}'.format(value)
    # used for result filenames
    return scenario


# 2 Setting Parameters simultaneously

def scen_gasgeothprice(site1, site2, value1, value2):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['commodity'].loc[(site1, 'Gas', 'Stock'), 'price'] = value1
        data['commodity'].loc[(site2, 'Geothermal', 'Stock'), 'price'] = value2
        return data

    scenario.__name__ = 'scenario_Gas-price-' + '{:04}'.format(value1) + '-GT-price-' + '{:04}'.format(value2)
    # used for result filenames
    return scenario


def scen_gasco2price(site1, site2, value1, value2):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['commodity'].loc[(site1, 'Gas', 'Stock'), 'price'] = value1
        data['commodity'].loc[(site2, 'CO2', 'Env'), 'price'] = value2
        return data

    scenario.__name__ = ('scenario_Gas-price-' + '{:04}'.format(value1) +
            '-co2-price-' + '{:04}'.format(value2))
    # used for result filenames
    return scenario


def scen_chppropgasprice(process, site, value1, value2):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['process_commodity'].loc[(process, 'Elec', 'Out'), 'ratio'] = (
                value1)
        data['process_commodity'].loc[(process, 'HeatHigh', 'Out'), 'ratio'] = (
                1 - 1.5 * value1)
        data['commodity'].loc[(site, 'Gas', 'Stock'), 'price'] = value2
        return data

    scenario.__name__ = ('scenario_CHP-ElecEff-' + '{:04,4f}'.format(value1) + 
            '-Gas-price-' + '{:04}'.format(value2))
    # used for result filenames
    return scenario


def scen_chppropco2price(process, site, eleceff, co2price):
    # scenario_name_suffix, site = string, value = float

    def scenario(data):
        data['process_commodity'].loc[(process, 'Elec', 'Out'), 'ratio'] = (
                eleceff)
        data['process_commodity'].loc[(process, 'HeatHigh', 'Out'), 'ratio'] = (
                1 - 1.5 * eleceff)
        data['commodity'].loc[(site, 'CO2', 'Env'), 'price'] = co2price
        return data

    scenario.__name__ = ('scenario_ElecEff-' + '{:04.4f}'.format(eleceff) +
            '-co2-price-' + '{:04}'.format(co2price))
    # used for result filenames
    return scenario


# SCENARIO LIST GENERATORS

def scen_1d_paramvar(scen_param, prop, min, max, steps):

    scenario_list = []

    for index in np.linspace(min, max, steps):
        scenario_list.append(scen_param(prop, index))
    
    return scenario_list


def scen_1d_log10paramvar(scen_param, prop, min, max, steps):
    # Careful! Use exponent für min and max values. 

    scenario_list = []

    for index in np.logspace(min, max, steps):
        scenario_list.append(scen_param(prop, index))
    
    return scenario_list
    

def scen_2d_paramvar(scen_param, prop1, min1, max1, steps1,
        prop2, min2, max2, steps2):

    scenario_list = []

    for index2 in np.linspace(min2, max2, steps2):
        for index1 in np.linspace(min1, max1, steps1):
            scenario_list.append(scen_param(prop1, prop2, index1, index2))
    
    return scenario_list


def scen_2d_log10paramvar(scen_param, prop1, min1, max1, steps1,
        prop2, min2, max2, steps2):
    # Careful! Use exponent for min and max values.

    scenario_list = []

    for index2 in np.logspace(min2, max2, steps2):
        for index1 in np.logspace(min1, max1, steps1):
            scenario_list.append(scen_param(prop1, prop2, index1, index2))
    
    return scenario_list


def scen_2d_linlog10paramvar(scen_param, prop1, min1, max1, steps1,
        prop2, min2, max2, steps2):
    # Careful! Use exponent for min and max values.

    scenario_list = []

    for index2 in np.logspace(min2, max2, steps2):
        for index1 in np.linspace(min1, max1, steps1):
            scenario_list.append(scen_param(prop1, prop2, index1, index2))
    
    return scenario_list
    