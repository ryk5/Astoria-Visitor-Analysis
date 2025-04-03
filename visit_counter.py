import pandas as pd


def count_visits(geoData_target, nyc_geoids):
    visits = {}
    for v in geoData_target['visitor_home_cbgs'].values:
        if v == '{}':
            continue
        else:
            tmp = v.replace('{"', '').replace('}', '').replace('"', '').replace('CA:','')
            tmp_ = tmp.split(',')
            for i in range(len(tmp_)):
                cbg = tmp_[i].split(':')[0]
                cnt = int(tmp_[i].split(':')[1])
                if cbg == 'CA':
                    print(v)
                if cbg in visits.keys():
                    visits[cbg] += cnt
                else:
                    visits.update({cbg:cnt})
    visits = pd.DataFrame(visits.items(), columns=['geoid','visitor_cnt'])
    visits = visits[visits['geoid'].isin(nyc_geoids)].reset_index(drop=True)
    print('There are visitors from {} unique cbgs zone'.format(len(visits.geoid.unique())))
    return visits
