import configparser
import os
import string


class ConfigUtil:
    config = configparser.RawConfigParser()

    @staticmethod
    def load(configFile):
        ConfigUtil.config.optionxform = str
        ConfigUtil.config.read(configFile, encoding='utf-8')

        for section in ConfigUtil.config.sections():
            for k, v in ConfigUtil.config.items(section):
                ConfigUtil.config[section][k] = string.Template(v).substitute(os.environ)

    @staticmethod
    def write(configFile):
        with open(configFile, 'w', encoding='utf-8') as configfile:
            ConfigUtil.config.write(configfile)

    @staticmethod
    def getItems(section):
        items = dict(ConfigUtil.config.items(section))

        return dict((k.lower(), v) for k, v in items.items())


ConfigUtil.load("config_2.ini")

# if __name__ == '__main__':
#     print("config is main")
#     ConfigUtil.load("config.ini")
#
#     """
#     print( ConfigUtil.config.get( "My" , "foodir1" , fallback="QQQ") )
#     print( ConfigUtil.config.items( "My") )
#     """
#
#     ConfigUtil.write('a.cfg')