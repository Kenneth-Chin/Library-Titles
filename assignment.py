import csv

# read input file with the csv module into a list of dictionaries
input_file = open('library-titles.csv')
library_titles_dict = list(csv.DictReader(input_file))


def cleanse_data(input_dict):
    """
    Cleanse the data based on requirement[1]:
    ISSN and e-ISSN must have 8 digits while ISBN and e-ISBN must have 10 or 13 digits
    reset those which are not conforming to the aforementioned digit formats to null
    """

    # iterate over each book in the database and check for each info that is not already null
    # if there are non-digit characters except 'x', 'X' and '-' in the info, then reset it to null
    # join the digits and wildcard 'X' from the info into a new string and check if it fulfills the length requirement
    # if not, change info to null in the dictionary
    for book in input_dict:
        if book["ISSN"] != "":
            if any(c not in "1234567890xX-" for c in book["ISSN"].strip()):
                book["ISSN"] = ""
            else:
                digit_string = ''.join([c for c in book["ISSN"] if c in "1234567890xX"])
                if len(digit_string) != 8:
                    book["ISSN"] = ""

        if book["e-ISSN"] != "":
            if any(c not in "1234567890xX-" for c in book["e-ISSN"].strip()):
                book["e-ISSN"] = ""
            else:
                digit_string = ''.join([c for c in book["e-ISSN"] if c in "1234567890xX"])
                if len(digit_string) != 8:
                    book["e-ISSN"] = ""

        if book["ISBN"] != "":
            if any(c not in "1234567890xX-" for c in book["ISBN"].strip()):
                book["ISBN"] = ""
            else:
                digit_string = ''.join([c for c in book["ISBN"] if c in "1234567890xX"])
                if len(digit_string) != 10 and len(digit_string) != 13:
                    book["ISBN"] = ""

        if book["e-ISBN"] != "":
            if any(c not in "1234567890xX-" for c in book["e-ISBN"].strip()):
                book["e-ISBN"] = ""
            else:
                digit_string = ''.join([c for c in book["e-ISBN"] if c in "1234567890xX"])
                if len(digit_string) != 10 and len(digit_string) != 13:
                    book["e-ISBN"] = ""


def info_string_matched(a, b):
    """
    A helper function for checking if two info strings of different books are equal or not
    while considering if there's a wildcard character 'X' in one of the strings
    """

    # remove '-' from both strings
    a = a.strip().replace('-', '')
    b = b.strip().replace('-', '')

    # convert lowercase x to uppercase X
    a = a.replace('x', 'X')
    b = b.replace('x', 'X')

    # if both strings are equal, simply return True
    if a == b:
        return True

    # if one of the strings contains 'X', check if substring before 'X' equal to the other string's substring
    # before index of X in first string, and check the same for substring after 'X'
    # if both are true, then info string is matched and return True, otherwise return False
    elif "X" in a:
        i = a.index("X")
        if a[:i] + a[i+1:] == b[:i] + b[i+1:]:
            return True
        else:
            return False
    elif "X" in b:
        i = b.index("X")
        if a[:i] + a[i+1:] == b[:i] + b[i+1:]:
            return True
        else:
            return False
    else:
        return False


def match_titles_and_merge(input_dict):
    """
    Match books that are of same titles into lists
    where they are categorized by their title name in a dictionary
    while merging same books from same DB into one item
    """
    title_matching_dict = dict()

    # go through each book and categorize them one by one
    for book in input_dict:
        # clean the book's title string and convert it into uppercase
        title = book["TITLE"].strip().upper()

        # if title has not been seen and added to the dictionary yet, then create the key and append an empty list to it
        if title not in title_matching_dict:
            title_matching_dict[title] = []

        # check in the existing list of the corresponding title if same book item from same database already exist
        is_distinct = True
        for book2 in title_matching_dict[title]:
            # if there is a book that is from same DB, and each info string is matched, then it is not distinct
            if book["DB"] == book2["DB"]:
                if info_string_matched(book["ISSN"], book2["ISSN"]) \
                 and info_string_matched(book["e-ISSN"], book2["e-ISSN"]) \
                 and info_string_matched(book["ISBN"], book2["ISBN"]) \
                 and info_string_matched(book["e-ISBN"], book2["e-ISBN"]):
                    is_distinct = False

        # if the book is distinct, then append the item to the list in the dictionary
        if is_distinct:
            title_matching_dict[title].append(book)

    return title_matching_dict


def find_duplication(input_dict):
    """
    Go through each matched title list and check if it satisfy the conditions to denote as a duplication:
    a) one match of either ISSN, e-ISSN, ISBN, or e-ISBN;
    b) all ISSN, e-ISSN, ISBN, and e-ISBN of these books are nulls.
    """
    duplication_list = []

    # keep track of the max books count in a duplication
    max_duplication_count = 0

    # iterate over each title and check for lists which have more than one book in them
    for title in input_dict:
        if len(input_dict[title]) > 1:
            is_duplication = False

            # if any of the info string matches for each book from the same title or every info is null,
            # then denote it as a duplication
            if input_dict[title][0]["ISSN"] != "" and all(info_string_matched(input_dict[title][0]["ISSN"], book["ISSN"]) for book in input_dict[title]):
                is_duplication = True
            elif input_dict[title][0]["e-ISSN"] != "" and all(info_string_matched(input_dict[title][0]["e-ISSN"], book["e-ISSN"]) for book in input_dict[title]):
                is_duplication = True
            elif input_dict[title][0]["ISBN"] != "" and all(info_string_matched(input_dict[title][0]["ISBN"], book["ISBN"]) for book in input_dict[title]):
                is_duplication = True
            elif input_dict[title][0]["e-ISBN"] != "" and all(info_string_matched(input_dict[title][0]["e-ISBN"], book["e-ISBN"]) for book in input_dict[title]):
                is_duplication = True
            elif all(book["ISSN"] == "" and book["e-ISSN"] == "" and book["ISBN"] == "" and book["e-ISBN"] == "" for book in input_dict[title]):
                is_duplication = True

            # if it's a duplication, add it to the output list after sorting alphabetically by its DB
            # and update the max book counts in a duplication
            if is_duplication:
                max_duplication_count = max(max_duplication_count, len(input_dict[title]))
                duplication_list.append(sorted(input_dict[title], key=lambda i: i["DB"]))

    return duplication_list, max_duplication_count


# use the functions defined to operate on the input data
# cleanse data, match titles and merge, then find duplication
cleanse_data(library_titles_dict)
library_titles_matched_dict = match_titles_and_merge(library_titles_dict)
duplicated_library_titles_list, max_duplicated_library_titles_count = find_duplication(library_titles_matched_dict)

# close the input file
input_file.close()

# create a new output file "duplication.csv"
with open("duplication.csv", 'w', newline='') as output_file:
    writer = csv.writer(output_file)

    # write the header of the csv file
    fieldnames = ["TITLE", "DB", "ISSN", "e-ISSN", "ISBN", "e-ISBN"] * max_duplicated_library_titles_count
    writer.writerow(fieldnames)

    # write each duplication from the list into a new row with the given formats
    # add null data at the end of row until each column is filled
    for duplication in duplicated_library_titles_list:
        row_output_list = []
        for book in duplication:
            row_output_list.extend([book["TITLE"], book["DB"], book["ISSN"], book["e-ISSN"], book["ISBN"], book["e-ISBN"]])
        row_output_list.extend([""] * ((6 * max_duplicated_library_titles_count) - len(row_output_list)))
        writer.writerow(row_output_list)

# ----------------------------------------------------------------------------------------------------------------------
import networkx as nx
import matplotlib.pyplot as plt

# create a dictionary where each key is a database
# and the corresponding value represent the number of titles in the database
db_node_dict = dict()
for title in library_titles_matched_dict:
    for book in library_titles_matched_dict[title]:
        if book["DB"] not in db_node_dict:
            db_node_dict[book["DB"]] = 0
        db_node_dict[book["DB"]] += 1
db_node_list = sorted(db_node_dict.items())
db_node_dict = dict(db_node_list)

# create an edge for every possible pair of nodes and initialize its value to 0
db_edge_dict = dict()
for i in range(len(db_node_list)):
    for j in range(i+1, len(db_node_list)):
        db_edge_dict[(db_node_list[i][0], db_node_list[j][0])] = 0

# get the database list for each duplicated title
duplicated_title_db_list = list()
for title in duplicated_library_titles_list:
    duplicated_title_db_list.append([])
    for book in title:
        duplicated_title_db_list[-1].append(book["DB"])

# calculate the number of duplicated titles between two databases for each edge
for pair in db_edge_dict:
    for db in duplicated_title_db_list:
        if pair[0] in db and pair[1] in db:
            db_edge_dict[pair] += 1

# remove edge which there is no connection between two databases
db_edge_dict = {k: v for k, v in db_edge_dict.items() if v != 0}

# create the network graph and add nodes and edges from the keys of dictionaries which were created
G = nx.Graph()
G.add_nodes_from(db_node_dict.keys())
G.add_edges_from(db_edge_dict.keys())

# define the color intensity for each edge based on number of duplicated titles between two nodes
colors = [c / max(db_edge_dict.values()) for c in db_edge_dict.values()]

options = {
    "node_color": "#A0CBE2",
    # define the size for each node based on number of titles in the database represented by the node
    "node_size": [s / max(db_node_dict.values()) * 10000 + 300 for s in db_node_dict.values()],
    "edge_color": colors,
    "width": 4,
    "edge_cmap": plt.cm.Blues,
    "with_labels": True,
}

# draw the graph with the design above
nx.draw_circular(G, **options)

# enlarge the image from default size
figure = plt.gcf()
figure.set_size_inches(10, 8)

# save the image into file "relation.png"
plt.savefig("relation.png")





