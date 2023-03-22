# -*- coding:utf-8 -*-
import json
import sys


def gen_dpkg_json():
    previous_dpkg = {}
    gen_dpkg_dict("previous", previous_dpkg)
    current_dpkg = {}
    gen_dpkg_dict("current", current_dpkg)
    new, trans = gen_new_and_tran_dict(previous_dpkg, current_dpkg)

    json_content = {"dpkg update list": trans, "dpkg add list": new}
    with open("report.json", "w") as f:
        f.write(json.dumps(json_content, indent=4))


def gen_dpkg_dict(time, dpkg_dist):
    with open(time + "_dpkg.txt") as f:
        for line in f.readlines():
            hello = line.split(' ')
            temp = []
            [temp.append(i) for i in hello if not i in temp]
            if len(temp) >= 4:
                dpkg_dist[temp[2]] = temp[3]


def gen_rpm_json():
    previous_rpm = {}
    gen_rpm_dict("previous", previous_rpm)
    current_rpm = {}
    gen_rpm_dict("current", current_rpm)
    new, trans = gen_new_and_tran_dict(previous_rpm, current_rpm)
    json_content = {"rpm update list": trans, "rpm add list": new}
    with open("report.json", "w") as f:
        f.write(json.dumps(json_content, indent=4))


def gen_rpm_dict(time, rpm_dist):
    with open(time + "_rpm.txt") as f:
        for line in f.readlines():
            split_list = line.replace('\n', '').split('-')
            version = split_list[len(split_list) - 1] + '-' + split_list[len(split_list) - 2]
            split_list.pop(len(split_list) - 1)
            split_list.pop(len(split_list) - 1)
            name = '-'.join(split_list)
            rpm_dist[name] = version


def gen_new_and_tran_dict(previous, current):
    new = {}
    trans = {}
    for k, v in current.items():
        if not previous.get(k):
            new[k] = "version: " + v
        elif previous.get(k) != v:
            trans[k] = ["previous version: " + previous.get(k), "current version: " + v]
        else:
            pass
    return new, trans


if __name__ == '__main__':
    package_mgmt_name = sys.argv[1]
    if package_mgmt_name == "rpm":
        gen_rpm_json()
    else:
        gen_dpkg_json()
