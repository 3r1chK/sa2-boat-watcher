from web.model.database import db
from web.model.Config import Config


class ConfigService:
    DEFAULT_CONFIG_KEYS = {
        'username': 'str',
        'api_key': 'str',
        'api_call_interval': 'int'  # TODO: implement calls limit
    }

    @staticmethod
    def has_all_entries():
        return sorted(ConfigService.get_all_as_dict().keys()) == sorted(ConfigService.DEFAULT_CONFIG_KEYS.keys())

    @staticmethod
    def get_all():
        return Config.query.all()

    @staticmethod
    def get_all_as_dict():
        all_configs = ConfigService.get_all()
        res = {}
        for config in all_configs:
            value = config.value
            if config.type == 'int':
                value = int(value)
            elif config.type == 'float':
                value = float(value)
            res[config.key] = value
        return res

    @staticmethod
    def get(config_key):
        if config_key in ConfigService.DEFAULT_CONFIG_KEYS.keys():
            db_config = ConfigService.get_all_as_dict()
            if config_key in db_config.keys():
                return db_config[config_key]
            else:
                return None

    @staticmethod
    def get_or_empty_string(config_key):
        res = ConfigService.get(config_key)
        if res is None:
            return ''
        return res

    @staticmethod
    def set(config_key, value):
        # Check if the config already exists
        existing_config = Config.query.filter_by(key=config_key).first()

        if existing_config:
            # If it exists, update the value
            existing_config.value = value
        else:
            # If it doesn't exist, create a new Config record
            new_config = Config(
                key=config_key,
                value=value,
                type=ConfigService.DEFAULT_CONFIG_KEYS[config_key]
            )
            db.session.add(new_config)

        # Commit the changes to the database
        db.session.commit()
