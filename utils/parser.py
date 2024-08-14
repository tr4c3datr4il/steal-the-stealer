from zipfile import ZipFile
from pathlib import Path
import json
import tempfile
import shutil



class Parser:
    def __init__(self, dump_path):
        self.dump_path = Path(dump_path)
        self.delimiter = [b'\t\t', b'|']
        self.dump_file = None
        # use mkdtemp so that the temp won't be deleted
        self.temp_dir = Path(tempfile.mkdtemp())
        self.initFile()

    def getInfo(self, filename):
        """Filename format:
        country_code ip time-date.zip
        time format: HHhMMmSSs-DD-MM-YYYY in UTC+7
        """

        country_code, ip, time_date = filename.split()
        time = time_date.split('-', 1)[0]
        time = time.replace('h', ':').replace('m', ':').replace('s', '')
        hour = time.split(':')[0].zfill(2)
        minute = time.split(':')[1].zfill(2)
        second = time.split(':')[2].zfill(2)
        time = f"{hour}:{minute}:{second}"
        date = time_date.split('-', 1)[1]
        date = date.replace('-', '/')
    
        return country_code, ip, time, date
    
    def decompressFile(self, file_path):
        # make temporary directory and extract to it
        tmp_dir = Path(self.temp_dir / file_path.stem)
        with ZipFile(file_path, 'r') as zip_file:
            zip_file.extractall(tmp_dir)

        return Path(tmp_dir)
        
    # we can use this to push the data to Elasticsearch
    def parseData(self, json_data: dict):
        with open(self.dump_file, '+a') as f:
            f.write(f"{json.dumps(json_data)}\n")

    def delFolder(self, path):
        shutil.rmtree(path)

    def delFile(self, path):
        Path.unlink(path)

    def initFile(self):
        self.dump_file = self.dump_path / 'dump.json'
        self.dump_file.touch(exist_ok=True)


class ProfileParser(Parser):
    def __init__(self, dump_path):
        super().__init__(dump_path)
        self.profiles = {
            "Braodo": "braodoParse",
            "None": "rawParse",
        }

    def processData(self, extracted_path, profile):
        if profile not in self.profiles:
            raise ValueError("Invalid profile")
        
        return getattr(self, self.profiles[profile])(extracted_path)        

    def braodoParse(self, extracted_path):
        for path in Path(extracted_path).rglob('pass.txt'):
            country_code, ip, time, date = self.getInfo(extracted_path.name.replace('.zip',''))
            with open(path, 'rb') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip() == b'':
                        continue
                    data = line.split(self.delimiter[0])
                    if len(data) < 2 or data[1].strip() == b'':
                        continue
                    url = data[0][4:].strip()
                    user_obj = data[1].split(self.delimiter[1])
                    if len(user_obj) < 2:
                        continue
                    username = user_obj[0].strip()
                    password = user_obj[1].strip()
                    if username == b'' or password == b'' or url == b'':
                        continue
                    
                    formatted_data = {
                        'time': time,
                        'date': date,
                        'country_code': country_code,
                        'ip': ip,
                        'url': str(url),
                        'username': str(username),
                        'password': str(password)
                    }

                    yield formatted_data
    
    def rawParse(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

            for line in lines:
                data = line.split()
                if len(data) < 4:
                    continue
                url = data[0]
                username = data[2]
                password = data[3]
                if username == '' or password == '' or url == '':
                    continue

                formatted_data = {
                    'url': str(url),
                    'username': str(username),
                    'password': str(password)
                }

                yield formatted_data