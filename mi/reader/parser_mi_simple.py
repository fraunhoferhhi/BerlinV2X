
import pandas as pd
from mobile_insight.analyzer import *
import logging


def unpack(input_dict, separator='_', prefix=''):
    '''
    Unpack any list of dictionaries at the topmost level of the message dictionary.
    The keys of the dictionaries are added at the root and filled with their concatenated values.
    Deeper lists and dictionaries are left as such.

    @param input_dict:
    @param separator:
    @param prefix:
    @return:
    '''

    output_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, list) and value:
            for index, sublist in enumerate(value, start=1):
                if isinstance(sublist, dict) and sublist:
                    for key_deep, value_deep in sublist.items():
                        try:
                            output_dict[key_deep].append(value_deep)
                        except AttributeError:
                            output_dict[key_deep] = [output_dict[key_deep], value_deep]
                        except KeyError:
                            output_dict[key_deep] = [value_deep]
                else:
                    output_dict[prefix+key+separator+str(index)] = value
        else:
            output_dict[prefix+key] = value

    return output_dict


#This file does the "actual" work of looking for events triggered by the MI analyzer and saving them within the class
class MiAnalyzer(Analyzer):

    def __init__(self):
   
        Analyzer.__init__(self)
        #include analyzers
        #self.include_analyzer("WcdmaRrcAnalyzer",[self.__on_event])
        #self.include_analyzer("LteRrcAnalyzer",[self.__on_event])
        self.add_source_callback(self.ue_event_filter)
        self.msg_count = 0

        self.df= {} #dicts with values  ##LOOK add whatever addiotional data you like here and in other places with "LOOK"
        self.columns={} #dict with columns for df  ##LOOK add whatever addiotional data you like here and in other places with "LOOK"
        print('Offline Analyzer initialized')

    def set_source(self, source):
        Analyzer.set_source(self, source)

    def ue_event_filter(self, msg):

        self.react_msg(msg)

    def react_msg(self, msg):
        #check for relevant messages here and do always the same except df name
        msg_dict = dict(msg.data.decode())
        msg_dict=unpack(msg_dict)
        if msg == 'LTE_PHY_PDSCH_Stat_Indication_monitor':
            logging.info(msg_dict.values())

        msg_dict['timestamp'] = msg_dict['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')

        if msg.type_id in self.columns:
            self.df[msg.type_id].append(list(msg_dict.values())) #append all values to lsit for dataframe
        else: # add to self
            self.columns[msg.type_id]=[]
            self.df[msg.type_id]=[list(msg_dict.values())]

        #check existing columns
        if (len(self.columns[msg.type_id])<len(list(msg_dict.keys())) ) :
            self.columns[msg.type_id]=list(msg_dict.keys()) #append all keys to column names

    def get_columns(self): #returns all available dfs

        keysList = [key for key in self.df]
        print(f"key list: {keysList}")
        return keysList
    
    def get_core_dataframe(self, dfname, cols=None):
        assert (self.df[dfname]), f'This dataframe ({dfname}) does not exist. Please pick from: {list(self.df.keys())} '
        df=pd.DataFrame(self.df[dfname])

        #for intra freq we have weird nearly empty cols
        colnames=self.columns[dfname]
        cnt=0
        while len(colnames) < df.shape[1]: #if for some reason colnames is shorter than our df cols, append sth
            colnames.append(f'fill_coll_{cnt}')
            cnt+=1 
            
        df=pd.DataFrame(self.df[dfname], columns =colnames)   
        
        if dfname=='LTE_PHY_PDSCH_Stat_Indication_monitor':
            logging.info(self.df[dfname])
            print(self.df[dfname].values())
        
        if cols is not None: #if cols is given, filter for this
            assert (set(cols).issubset(df.columns)), f'These columns are not avaialable. Please pick from: {self.columns[dfname]}. (You tried {cols}) '
            df=df[cols].copy()   #filter for columns of interest
        
        return df
