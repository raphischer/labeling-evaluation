import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd


def build_dict_from_excel(excel_file, discard):
    codes = pd.read_excel(excel_file)
    current_keys, current_level, frequencies = [], -1, {}
    for _, row in codes.iterrows():
        for idx, v in enumerate(row.__iter__()):
            if len(v.strip()) == 0:
                continue
            if idx == current_level:
                current_keys[-1] = v
                break
            elif idx < current_level:
                # update current keys and level
                current_keys = current_keys[:idx] + [v]
                current_level = idx
                break
            else: # idx > current_level
                current_level += 1
                current_keys.append(v)
                break
        if current_keys[-1] not in discard:
            try:
                frequencies[tuple(current_keys)] = int(row.values.tolist()[-1])
            except Exception:
                frequencies[tuple(current_keys)] = 0
    return frequencies


def build_tree_from_dict(data):
    tree = {}
    for key_tuple, frequency in data.items():
        current_level = tree
        for lvl, key in enumerate(key_tuple):
            if key not in current_level:
                current_level[key] = {"name": key, "frequency": frequency, "sub_frequency": 0, "level": lvl, "children": {}}
            current_level = current_level[key]["children"]
    tree = list(tree.values())[0]
    tree['frequency'] = 0

    def add_subtree_freqs(tree):
        if len(tree["children"]) == 0:
            return tree["frequency"]
        else:
            for _, sub_tree in tree["children"].items():
                tree['sub_frequency'] += add_subtree_freqs(sub_tree)
        return tree['sub_frequency'] + tree['frequency']
    
    add_subtree_freqs(tree)
    return tree


def recursively_walk_tree(tree, print_nodes=True):
    freq = str(tree['frequency'])
    if tree['sub_frequency'] > 0:
        freq += f"+{tree['sub_frequency']}"
    node_str = "    " * tree['level'] + f"{tree['name']} ({freq})"
    if print_nodes:
        print(node_str)
    if len(tree["children"]) == 0:
        return 1
    else:
        sub_size = 0
        for sub_tree in tree['children'].values():
            sub_size += recursively_walk_tree(sub_tree, print_nodes=print_nodes)
        return sub_size
    

def merge_rare(tree, threshold=2):
    new = {'name': tree['name'], 'frequency': tree['frequency'], 'sub_frequency': tree['sub_frequency'], 'level': tree['level'], 'children': {}}
    other, keep = 0, []
    for child in tree['children'].values():
        child_freq = child['frequency'] + child['sub_frequency']
        if child_freq <= threshold:
            other += child_freq
        else:
            keep.append( (child_freq, merge_rare(child)) )
    # store in reversed order
    if other > 0:
        new['children']['Others'] = {'name': 'Others', 'frequency': other, 'sub_frequency': 0, 'level': tree['level'] + 1, 'children': {}}
    for _, child in sorted(keep, key=lambda x: x[0]):
        new['children'][child['name']] = child
    return new


def generate_qtree_code(node):    
    sub_freq = '' if node["sub_frequency"] == 0 else f'+{node["sub_frequency"]}'
    node_label = f'{{{node["name"]} ({node["frequency"]}{sub_freq})}}'
    if len(node["children"]) < 2:
        return f"[.{node_label} ]"
    else:
        children_code = " ".join(generate_qtree_code(child) for child in node["children"].values())
        return f"[.{node_label} {children_code} ]"


discard = ['ANON', 'Katha dky', 'Money Quotes']
excel_dict = build_dict_from_excel('MAXQDA24 project - Codesystem.xlsx', discard)
tree = build_tree_from_dict(excel_dict)
tot_num, tot_freqs = str(recursively_walk_tree(tree)), str(tree['frequency'] + tree['sub_frequency'])
tree_merged = merge_rare(tree)

# generate overview table
fam_quotes = {
    'General Codes': ('this is some weird quote', 'I2'),
    'Exemplary Labels': ('oh look, here is another quote!', 'I5')
}
table_rows = [' $AND '.join(['Code Family', 'RQ', '\#Codes', '\#Occ', 'Quote']) + r' \\', r'\toprule']
for fam, fam_codes in tree['children'].items():
    for code, subtree in fam_codes['children'].items():
        quote = fam_quotes.get(code, ('', 'n.a.'))
        depth, fmt_quote = str(recursively_walk_tree(subtree)), r'\emph{' + quote[0] + r'}' + f' ({quote[1]})'
        freq = str(subtree['frequency'] + subtree['sub_frequency'])
        table_rows.append(' $AND '.join([code, fam.split(' ')[0], depth, freq, fmt_quote]) + r' \\')
table_rows = table_rows + [r'\midrule', ' $AND '.join(['Total', ' ', tot_num, tot_freqs, ' '])]
tab_final = r'\begin{tabular}{lllll}' + '\n    ' + '\n    '.join(table_rows) + '\n' + r'\end{tabular}'
with open('paper_results/tab_codesystem_overview.tex', 'w') as tab:
    tab.write(tab_final.replace('&', '\&').replace('$AND', '&'))

# generate code family trees
for fam, fam_codes in tree_merged['children'].items():
    for code, subtree in fam_codes['children'].items(): 
        tikz_code = '\n'.join([
            r'\begin{tikzpicture}[grow=right,level distance=200pt,scale=1,transform shape]',
            r'\Tree ' + generate_qtree_code(subtree).replace('&', r'\&'),
            r'\end{tikzpicture}' ])
        with open(f'paper_results/codes_{fam.split(" ")[0]}_{code.replace(" ", "_")}.tex', 'w') as tf:
            tf.write(tikz_code)

data = pd.read_csv('interviewees.csv')

tab_cols = ['Job Title', 'Company Type', 'Employees', 'Gender', 'Age', 'AI Skills']
table_rows = [' $AND '.join(['ID'] + tab_cols) + r' \\', r'\toprule']
for idx, row in data[tab_cols].iterrows():
    values = [f'I{idx+1}'] + row.values.astype(str).tolist()
    table_rows.append(' $AND '.join(values) + r' \\')
tab_final = r'\begin{tabular}{lllllll}' + '\n    ' + '\n    '.join(table_rows) + '\n' + r'\end{tabular}'
with open('paper_results/tab_interviewees.tex', 'w') as tab:
    tab.write(tab_final.replace('&', '\&').replace('$AND', '&'))




# data = data.drop('Job Title', axis=1)

# fig = make_subplots(
#     rows=2, cols=2,
#     subplot_titles=data.columns.tolist()
# )

# # Add a histogram for each column
# for i, column in enumerate(data.columns):
#     if data[column].dtype == 'object':
#         print(column)
#         # Categorical data: bar chart of counts
#         fig.add_trace(
#             px.histogram(data, x=column).data[0], 
#             row=i//2+1, col=i%2 + 1
#         )
#     else:
#         # Numeric data: histogram
#         fig.add_trace(
#             px.histogram(data, x=column, nbins=10).data[0], 
#             row=i//2+1, col=i%2 + 1
#         )

# # Update layout
# fig.update_layout(
#     title_text="Distribution of Interviewee Attributes",
#     showlegend=False,
#     height=500, width=600,
#     template='plotly_white'
# )

# # Show plot
# fig.show()
