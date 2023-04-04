import os
import threading, queue
import queue
from kafka import KafkaConsumer
import time
import datetime
import json
from celery import Celery
import requests
from redis import StrictRedis

import logging
from logging.handlers import RotatingFileHandler

Rthandler = RotatingFileHandler('/home/apm/consumer_to_redis/apm_consumer_to_redis_ext.log', maxBytes=10*1024*1024,backupCount=5)
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)
logging.getLogger('').setLevel(logging.INFO)


app_win_keys = []
r = requests.get("http://cn/v1/api/external/getAllProjects?platform=crasheye&external=-1", headers={'Authorization': 'access_token c200a2d3-e624-47e0-a0bb-232fe4bbcadf'})
app_info = r.json()
apps = app_info['result']
for a_p_info in apps:
    if 'related' in a_p_info:
        for a_p_k_info in a_p_info['related']:
            if 'client' in a_p_k_info and a_p_k_info['client'] == 'pc' and 'appKey' in a_p_k_info:
                app_win_keys.append(a_p_k_info['appKey'])

logging.info(app_win_keys)

apmapp = Celery(backend="redis://localhost:6379/5", broker="redis://localhost:6379/6")

def f():
    consumer = KafkaConsumer("qcapm",  bootstrap_servers=["172.18.7.120:9092"])
    while True:
        c_msgs = consumer.poll(max_records=500).values()
        p_msg_infos = []
        for m_bo in c_msgs:
            for msg in m_bo:
                try:
                    c_msg = msg.value.decode("utf-8")
                    d_msg = json.loads(c_msg)

                    if 'sif' in d_msg:
                        if d_msg['sif'] == 'Startup':
                            continue

                    logging.info(' d_msg[%s]', d_msg)

                    if 'appKey' in d_msg and d_msg['appKey'] and 'stime' in d_msg and d_msg[
                        'stime'] and 'appVersion' in d_msg and d_msg['appVersion']:
                        logging.info('sned msg to celery start')

                        d_msg['hour'] = int(datetime.datetime.now().hour)

                        if 'dcm' in d_msg:
                            continue

                        if 'aid' in d_msg:
                            d_msg['accountId'] = d_msg['aid']

                        if 'Oversea' in d_msg and d_msg['Oversea'] == '1':
                            d_msg['glocaltion'] = '2'
                        elif 'Oversea' in d_msg and d_msg['Oversea'] != '1':
                            d_msg['glocaltion'] = '1'

                        if 'gpd' not in d_msg:
                            d_msg['gpd'] = '0'

                        if 'dvm' in d_msg:
                            d_msg['deviceMode'] = d_msg['dvm']
                        if 'pcn' in d_msg:
                            d_msg['packageName'] = d_msg['pcn']
                        if 'cst' in d_msg:
                            d_msg['clientStartTime'] = d_msg['cst']
                        if 'dvg' in d_msg:
                            d_msg['deviceGrade'] = d_msg['dvg']
                        if 'din' in d_msg:
                            d_msg['definition'] = d_msg['din']
                        if 'cdin' in d_msg:
                            d_msg['currentDefinition'] = d_msg['cdin']
                        if 'dcc' in d_msg:
                            d_msg['device_cpu'] = d_msg['dcc']
                        if 'dcg' in d_msg:
                            d_msg['device_gpu'] = d_msg['dcg']
                        if 'sdkv' in d_msg:
                            d_msg['sdkVersion'] = d_msg['sdkv']

                        if 'sif' in d_msg:
                            d_msg['sceneIdentifier'] = d_msg['sif']
                        if 'sifid' in d_msg:
                            d_msg['sceneIdentifierID'] = d_msg['sifid']
                        if 'sst' in d_msg:
                            d_msg['sceneStartTime'] = d_msg['sst']
                        if 'sut' in d_msg:
                            d_msg['sceneUseTime'] = d_msg['sut']
                        if 'scc' in d_msg:
                            d_msg['sceneCollectDataCount'] = d_msg['scc']
                        if 'sfc' in d_msg:
                            d_msg['sceneFrameCount'] = d_msg['sfc']
                        if 'slt' in d_msg:
                            d_msg['sceneLoadTime'] = d_msg['slt']
                        if 'fsc' in d_msg:
                            d_msg['fpsSwingCount'] = d_msg['fsc']
                        if 'lfc' in d_msg:
                            d_msg['lowFpsCount'] = d_msg['lfc']
                        if 'jfc' in d_msg:
                            d_msg['jankFrameCount'] = d_msg['jfc']
                        if 'bjc' in d_msg:
                            d_msg['bigJankCount'] = d_msg['bjc']
                        if 'dfc' in d_msg:
                            d_msg['dropFpsCount'] = d_msg['dfc']

                        if 'psm' in d_msg:
                            d_msg['pssMemory'] = d_msg['psm']
                        if 'vsm' in d_msg:
                            d_msg['vssMemory'] = d_msg['vsm']
                        if 'temp' in d_msg:
                            d_msg['temperature'] = d_msg['temp']
                        if 'cpuu' in d_msg:
                            d_msg['cpuUsage'] = d_msg['cpuu']
                        if 'psm' in d_msg:
                            d_msg['pssMemory'] = d_msg['psm']
                        if 'ttm' in d_msg:
                            d_msg['totalMemory'] = d_msg['ttm']
                        if 'ltm' in d_msg:
                            d_msg['leftMemory'] = d_msg['ltm']
                        if 'usm' in d_msg:
                            d_msg['usedMemory'] = d_msg['usm']
                        if 'bat' in d_msg:
                            d_msg['battery'] = d_msg['bat']
                        if 'aam' in d_msg:
                            d_msg['availableMemory'] = d_msg['aam']

                        if 'eventId' in d_msg and (
                                d_msg['eventId'] == 'perf' or d_msg[
                            'eventId'] == 'sceneinfo') and 'definition' not in d_msg:
                            continue

                        if 'fps' in d_msg:
                            d_msg['ffps'] = float(d_msg['fps'].replace(',', '.'))
                            d_msg['fps'] = int(float(d_msg['fps'].replace(',', '.')))

                        if 'avefps' in d_msg:
                            d_msg['avefps'] = float(d_msg['avefps'].replace(',', '.'))

                        if 'egtime' in d_msg:
                            d_msg['egtime'] = int(float(d_msg['egtime'].replace(',', '.')))

                        if 'fpsSwingCount' in d_msg:
                            d_msg['fpsSwingCount'] = int(float(d_msg['fpsSwingCount'].replace(',', '.')))
                        if 'pssMemory' in d_msg:
                            d_msg['pssMemory'] = int(float(d_msg['pssMemory'].replace(',', '.')))
                        if 'vssMemory' in d_msg:
                            d_msg['vssMemory'] = int(float(d_msg['vssMemory'].replace(',', '.')))
                        if 'lowFpsCount' in d_msg:
                            d_msg['lowFpsCount'] = int(float(d_msg['lowFpsCount'].replace(',', '.')))
                        if 'sceneUseTime' in d_msg:
                            d_msg['sceneUseTime'] = int(float(d_msg['sceneUseTime'].replace(',', '.')))
                        if 'bigJankCount' in d_msg:
                            d_msg['bigJankCount'] = int(float(d_msg['bigJankCount'].replace(',', '.')))
                        if 'jankFrameCount' in d_msg:
                            d_msg['jankFrameCount'] = int(float(d_msg['jankFrameCount'].replace(',', '.')))
                        if 'sceneLoadTime' in d_msg:
                            d_msg['sceneLoadTime'] = int(float(d_msg['sceneLoadTime'].replace(',', '.')))
                        if 'dropFpsCount' in d_msg:
                            d_msg['dropFpsCount'] = int(float(d_msg['dropFpsCount'].replace(',', '.')))
                        if 'battery' in d_msg:
                            d_msg['battery'] = int(float(d_msg['battery'].replace(',', '.')))
                        if 'temperature' in d_msg:
                            d_msg['temperature'] = int(float(d_msg['temperature'].replace(',', '.')))

                        if d_msg['appKey'] in app_win_keys:
                            if 'isNote' in d_msg:
                                d_msg['devicetype'] = d_msg['isNote']
                            if 'isnote' in d_msg:
                                d_msg['devicetype'] = d_msg['isnote']
                            if 'devicetype' not in d_msg:
                                d_msg['devicetype'] = '0'

                        if 'devicetype' not in d_msg:
                            d_msg['devicetype'] = 'null'

                        if 'smt' in d_msg:
                            d_msg['smt'] = float(d_msg['smt'].replace(',', '.'))

                        if 'pcu' in d_msg:
                            d_msg['pcu'] = float(d_msg['pcu'].replace(',', '.'))

                        if 'definition' in d_msg and d_msg['definition'] == 'null':
                            logging.info('definition is null d_msg[%s]', d_msg)
                            continue
                        # if 'deviceGrade' in d_msg and d_msg['deviceGrade'] == 'null':
                        #    logging.info('deviceGrade is null d_msg[%s]', d_msg)
                        #    continue
                        if 'deviceGrade' not in d_msg:
                            d_msg['deviceGrade'] = 'null'

                        if 'deviceMode' in d_msg and d_msg['deviceMode'] == 'null':
                            logging.info('deviceMode is null d_msg[%s]', d_msg)
                            continue
                        if 'sceneIdentifier' in d_msg and d_msg['sceneIdentifier'] == 'null':
                            logging.info('sceneIdentifier is null d_msg[%s]', d_msg)
                            continue

                        if 'eventId' in d_msg and (d_msg['eventId'] == 'perf' or d_msg[
                            'eventId'] == 'sceneinfo') and 'sceneIdentifier' not in d_msg:
                            continue

                        if d_msg['appKey'] in ['b10070c0', 'dkzg4end', 'ba3ace60']:
                            if 'device_cpu' in d_msg:
                                if 'x86' in d_msg['device_cpu']:
                                    logging.info('ignro appKey[%s]  device_cpu[%s]', d_msg['appKey'],
                                                 d_msg['device_cpu'])
                                    continue

                                if 'armv7' in d_msg['device_cpu'] and 'definition' in d_msg and d_msg['definition'] == '3':
                                    logging.info('ignro appKey[%s]  definition[%s]  device_cpu[%s]', d_msg['appKey'],
                                                 d_msg['definition'], d_msg['device_cpu'])
                                    continue

                        p_msg_infos.append(d_msg)

                except Exception as e:
                    logging.info("upload.tasks.upload_version_analysis Exception[%s] d_msg[%s]", str(e), d_msg)
                    continue

        if p_msg_infos and len(p_msg_infos) > 0:
            try:
                #print('p_msg_infos[%s]' % len(p_msg_infos))
                ret = apmapp.send_task('upload.batch_tasks.upload_version_analysis_ext', (p_msg_infos,),
                                 queue='apm_service:upload:analysis')
                #print(ret)
            except Exception as e:
                logging.info("upload.tasks.upload_version_analysis Exception[%s]", str(e))
                apmapp = Celery(backend="redis://localhost:6379/5", broker="redis://localhost:6379/6")


f()


