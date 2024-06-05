import configparser


class App:
    __conf = None
    
    @staticmethod
    def config():
        if App.__conf is None:
            App.__conf = configparser.ConfigParser()
            App.__conf.read('CONFIG.ini')
        return App.__conf

if __name__ == "__main__":
    a = App.config().getint(section="APP", option="")
    print(a)