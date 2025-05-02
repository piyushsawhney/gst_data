import json

import numpy as np
import pandas as pd
import pyzipper


def unzip_file(zip_file_path, password, unzip_file_path):
    print(f"Extracting {zip_file_path}")
    with pyzipper.AESZipFile(zip_file_path) as zf:
        if password:
            zf.extractall(path=unzip_file_path, pwd=password.encode('utf-8'))
        else:
            zf.extractall(path=unzip_file_path)
        return [file_name for file_name in zf.namelist()]


def process_cams_invoice_dataframe(dataframe):
    with open('../cams_amc_code.json', 'r') as f:
        mapping_dict = json.load(f)
    updated_df = dataframe[
        ['INVOICE_DATE', 'INVOICE_NUMBER', 'AMC_CODE', 'CUSTOMER_GSTIN', 'INVOICE_VALUE', 'TAX_AMOUNT'
         ]].copy()
    updated_df['INVOICE_DATE'] = pd.to_datetime(updated_df['INVOICE_DATE'], format='%m/%d/%Y %I:%M:%S %p')
    updated_df['INVOICE_DATE'] = updated_df['INVOICE_DATE'].dt.strftime('%d-%m-%Y')
    updated_df['INVOICE_NUMBER'] = np.nan
    updated_df.loc[:, 'TAXABLE_AMOUNT'] = updated_df['INVOICE_VALUE'] - updated_df['TAX_AMOUNT']
    updated_df.loc[:, 'AMC_CODE'] = updated_df['AMC_CODE'].map(mapping_dict)
    updated_df = updated_df.rename(columns={'AMC_CODE': 'AMC_NAME'})
    updated_df = updated_df.rename(columns={'CUSTOMER_GSTIN': 'AMC_GSTIN'})
    return updated_df[['INVOICE_DATE', 'INVOICE_NUMBER', 'AMC_GSTIN', 'AMC_NAME', 'TAXABLE_AMOUNT']]


def process_cams_invoice():
    cams_invoice_zip_path = "../gst_reports/cams/invoice/zip/cams_invoice.zip"
    cams_invoice_unzip_file_path = "../gst_reports/cams/invoice/csv"
    file_names = unzip_file(cams_invoice_zip_path, "123456", cams_invoice_unzip_file_path)
    print(file_names)
    for filename in file_names:
        csv_file_path = f"{cams_invoice_unzip_file_path}/{filename}"
        df = pd.read_csv(csv_file_path, quotechar="'")
        processed_df = process_cams_invoice_dataframe(df)
        processed_df.to_excel('output.xlsx', index=False)

    # Unzip file
    # Rename CSV


process_cams_invoice()
