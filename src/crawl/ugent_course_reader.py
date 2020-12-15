import re

import src.crawl.unicrawl.spiders.config.settings as s
import utils as u

SEPARATOR_FIRST_AND_SECOND_PART = 'Offered in the following programmes in  2020-2021crdtsoffering'

LECTURERS_PARAGRAPH_SPLITTER = f"Lecturers in academic year {s.YEAR}-{int(s.YEAR) + 1}"
OTHER_CATEGORIES_SEPARATORS = ["Course offerings and teaching methods",
                               "Offered in the following programmes in",
                               "Course size"]

# Read PDF file
page_content = u.read_pdf()

# mapping : [prerequisite,theme,goal,content,method,evaluation other, resources,biblio,faculty,anacs,shortname,class,location, teachers,language]
course = {}

if SEPARATOR_FIRST_AND_SECOND_PART in page_content:
    part_1_main_infos = page_content[:page_content.find(SEPARATOR_FIRST_AND_SECOND_PART) +
                                 len(SEPARATOR_FIRST_AND_SECOND_PART)]
# 1 - NAME
course["name"] = re.split('[()]', part_1_main_infos)[0] #TODO: Look for exceptions
# 2 - ID
course["id"] = re.split('[()]', part_1_main_infos)[1] #TODO: Look for exceptions

# Extract infos from part 1 of the document [credits, study_time, year] ------------------------------

# 3 - TEACHERS
teacher_paragraph = part_1_main_infos.split(LECTURERS_PARAGRAPH_SPLITTER)[1]
print("TEACHER_PARAGRAPH BEFORE SPLIT: ", teacher_paragraph)

for splitter in OTHER_CATEGORIES_SEPARATORS:
    teacher_paragraph = teacher_paragraph.split(splitter)[0]
print("TEACHER_PARAGRAPH AFTER SPLIT: ", teacher_paragraph)
#TODO: Improve this
course["teacher"] = teacher_paragraph


# 4 - ECTS
index = page_content.find('Credits')
substring = page_content[index:index+len('Credits')+ 20]
for part in re.split('[ (]', substring):
    if u.is_float(part):
        course["ects"] = float(part)
        break

# BONUS - Study time
index = page_content.find('Study time')
substring = page_content[index:index+len('Study time')+ 20]
for part in re.split('[ (]', substring):
    if u.is_float(part):
        course["study_time"] = float(part)
        break

# 9 - YEAR
index = page_content.find('academic year ')
substring = page_content[index:index+len('academic year ')+ 20]
course["year"] = substring[len('academic year '):len('academic year ')+9]

# ---------------------------------------------------------------------------------------------

separator = str(int(course["ects"])) + "A"
index = page_content.rindex(separator)
part_2_courses_list = page_content[len(part_1_main_infos):index]
part_3_detailed_infos = page_content[index + len(separator):]

# ---------------------------------------------------------------------------------------------

# Extract infos from part 2 of the document [list of formations where course is dispensed] -----------------------

course["formation"] = part_2_courses_list.split(separator)

# Extract infos from part 3 of the document [ ... ] -----------------------

# For debugging purpose
course["part_1_main_infos"] = part_1_main_infos
course["part_2_courses_list"] = part_2_courses_list
course["part_3_detailed_infos"] = part_3_detailed_infos

for key, value in course.items():
    print("{}: {}\n".format(key, value))


