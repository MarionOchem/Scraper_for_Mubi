import csv
from unidecode import unidecode
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def export_data(data, csv_filename, sql_filename, table_name):
    logger.info('Starting to export data')
    # Create columns 
    columns = []
    columns.extend(['id', 'title'])
    for attributes in data.values():
        for key in attributes.keys():
            if key not in columns:
                columns.append(key)
    

    # Write CSV
    logger.info('Create .csv')
    with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=columns) # order and names of columns
        dict_writer.writeheader()
        id_counter = 1
        for title, attributes in data.items():
            normalized_attributes = {key: unidecode(value) if isinstance(value, str) else value for key, value in attributes.items()}
            row = {'id': id_counter, 'title': unidecode(title), **normalized_attributes} # create a single dictionary for each row
            dict_writer.writerow(row)
            id_counter += 1


   # Write SQL file
    logger.info('Create .sql')
    with open(sql_filename, 'w', encoding='utf-8') as sql_file:
        # Write CREATE TABLE statement
        sql_columns = ', '.join([f'{col} TEXT' for col in columns if col != 'id'])
        create_table_sql = f'CREATE TABLE {table_name} (id SERIAL PRIMARY KEY, {sql_columns});\n'
        sql_file.write(create_table_sql)

        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)})"
        for idx, (title, attributes) in enumerate(data.items(), start=1):
        # Prepare values in the correct order
            values = tuple([idx] + [title] + [attributes.get(col, '') for col in columns if col != 'title' and col != 'id'])
            insert_values_sql = f"({', '.join(map(repr, values))})"
            if idx == 1:
                sql_file.write(f"{insert_sql} \nVALUES \n    {insert_values_sql},\n")
            elif idx < len(data):  # Add comma for all but the last row
                sql_file.write(f"    {insert_values_sql},\n")
            else:  # Last row: add semicolon instead of comma
                sql_file.write(f"    {insert_values_sql};\n")


    logger.info(f'Exported movies data to {csv_filename} and {sql_filename}')


