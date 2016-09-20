#!/usr/bin/env python3
import csv
import argparse
from os import path, listdir
from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--withprofile', action='store_true')
    parser.add_argument('--prefix', default='https://www.facebook.com/profile.php?id=')
    parser.add_argument('-e', '--exclusions', default='')
    parser.add_argument('--noprint', action='store_true')
    args = parser.parse_args()

    def collect_usos_students(students_set):
        def collect_students(filename, students_set):
            with open(filename) as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                next(reader)
                for student in reader:
                    if not int(student[3]):
                        students_set.add((student[1], student[0]))

        for data_filename in filter(lambda x: not path.isdir(path.join('data', x)) and x[-4:] == '.csv', listdir('data')):
            collect_students(path.join('data', data_filename), students_set)


    def collect_fb_members(fb_members_set):
        with open('data/group_members.html') as fb_html:
            exclusions = set()
            if args.exclusions:
                with open(args.exclusions) as exclusions_file:
                    exclusions = set(exclusions_file.readline())

            soup = BeautifulSoup(fb_html.read(), 'html.parser')
            divs = soup.findAll("div", {"class": ["fsl"]})
            for div in divs:
                if args.withprofile:
                    href = div.a['href']
                    if "profile.php" in href:
                        # len('https://www.facebook.com/profile.php?id=') == 40
                        # len('&fref=pb_other') == 14
                        profile = href[40:-14]
                    else:
                        profile = href[len('https://www.facebook.com/'):-14]
                if div.a.text not in exclusions:
                    text_split = div.a.text.split(' ')
                    if len(text_split) == 2:
                        fb_members_set.add(tuple(text_split if not args.withprofile else text_split + [profile]))
                    elif len(text_split) == 3:
                        fb_members_set.add(
                            (text_split[0], text_split[2]) if not args.withprofile else (text_split[0], text_split[2], profile)
                        )

    usos_students = set()
    collect_usos_students(usos_students)
    print("Number of USOS students: %s" % len(usos_students))

    fb_members = set()
    collect_fb_members(fb_members)
    print("Number of facebook group members: %s" % len(fb_members))

    if args.withprofile:
        bad_members = fb_members.copy()
        for fb_member in fb_members:
            if fb_member[0:2] in usos_students:
                bad_members.remove(fb_member)
    else:
        bad_members = fb_members - usos_students

    print("Number of bad members: %s" % len(bad_members))
    if not args.noprint:
        print("BAD MEMBERS:")
        for bad_member in sorted(bad_members, key=lambda x: x[0] + x[1]):
            if args.withprofile:
                print("  %s %s," % bad_member[:2], "%s%s" % (args.prefix, bad_member[2]))
            else:
                print("  %s %s" % bad_member)

if __name__ == '__main__':
    main()