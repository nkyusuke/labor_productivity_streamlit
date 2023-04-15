import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import plotly.express as px
import warnings
warnings.simplefilter("ignore") 


df_company=pd.read_csv("./産業構造_全産業_全産業の構造_企業数_市区町村_中分類.csv",encoding="shift_jis") 
df_sales=pd.read_csv("./産業構造_全産業_全産業の構造_売上高（企業単位）_市区町村_中分類.csv",encoding="shift_jis")
df_labor=pd.read_csv("./産業構造_全産業_全産業の構造_従業者数（企業単位）_市区町村_中分類.csv",encoding="shift_jis")
df_value=pd.read_csv("./産業構造_全産業_全産業の構造_付加価値額_市区町村_中分類.csv",encoding="shift_jis")
df_labor_productivity=pd.read_csv("./産業構造_全産業_労働生産性_市区町村_中分類.csv",encoding="shift_jis")


x = df_labor_productivity[(df_labor_productivity["集計年"]==2012)&(df_labor_productivity["都道府県名"]=="栃木県")&(df_labor_productivity["市区町村名"]=="栃木市")].sort_values(by="労働生産性(千円/人)").drop_duplicates(subset="業種中分類名", keep="first")
y = df_labor_productivity.loc[~((df_labor_productivity["集計年"]==2012)&(df_labor_productivity["都道府県名"]=="栃木県")&(df_labor_productivity["市区町村名"]=="栃木市"))]
df_labor_productivity = pd.concat([x, y])


df_labor_productivity["労働生産性(千円/人)"]=df_labor_productivity["労働生産性(千円/人)"].replace("X",np.nan)
df_labor_productivity["労働生産性(千円/人)"]=df_labor_productivity["労働生産性(千円/人)"].replace("-",np.nan)
df_labor_productivity["労働生産性(千円/人)"]=df_labor_productivity["労働生産性(千円/人)"].replace("#NUM!",np.nan)


df_labor_productivity_master=df_labor_productivity.dropna(subset=["労働生産性(千円/人)"],axis=0)


df_company.rename(columns={"都道府県CD":"都道府県コード","市区町村CD":"市区町村コード","産業大分類CD":"産業大分類コード","業種中分類CD":"業種中分類コード"},inplace=True)
df_labor.rename(columns={"都道府県CD":"都道府県コード","市区町村CD":"市区町村コード","産業大分類CD":"産業大分類コード","業種中分類CD":"業種中分類コード"},inplace=True)


merge_company=pd.merge(df_labor_productivity_master,df_company,on=["集計年","都道府県コード","都道府県名","市区町村コード","市区町村名","産業大分類コード","産業大分類名","業種中分類コード","業種中分類名"])
merge_company_sales=pd.merge(merge_company,df_sales,on=["集計年","都道府県コード","都道府県名","市区町村コード","市区町村名","産業大分類コード","産業大分類名","業種中分類コード","業種中分類名"])
merge_company_sales_labor=pd.merge(merge_company_sales,df_labor,on=["集計年","都道府県コード","都道府県名","市区町村コード","市区町村名","産業大分類コード","産業大分類名","業種中分類コード","業種中分類名"])
merge_company_sales_labor_value=pd.merge(merge_company_sales_labor,df_value,on=["集計年","都道府県コード","都道府県名","市区町村コード","市区町村名","産業大分類コード","産業大分類名","業種中分類コード","業種中分類名"])


dataset=merge_company_sales_labor_value
dataset=dataset.astype({"労働生産性(千円/人)":float,"企業数":float,"売上高(百万円)":float,"企業単位_従業者数（人）":float,"付加価値額(百万円)":float,})


st.title("日本の労働生産性データダッシュボード")
year_list=dataset["集計年"].unique()
pref_list=dataset["都道府県名"].unique()


st.header("■集計年別の労働生産性の推移")
dataset_jp=pd.DataFrame(columns=["集計年","都道府県名","労働生産性(千円/人)"])
for year in year_list:
    x=dataset.loc[dataset["集計年"]==year,"企業数"].multiply(dataset["労働生産性(千円/人)"]).sum()
    y=dataset.loc[dataset["集計年"]==year,"企業数"].sum()
    z=x/y
    dataset_jp=dataset_jp.append({"集計年":year,"都道府県名":"全国","労働生産性(千円/人)":z},ignore_index=True)    
dataset_pref=pd.DataFrame(columns=["集計年","都道府県名","労働生産性(千円/人)"])
for year in year_list:
    for pref in pref_list:
        x=dataset.loc[(dataset["集計年"]==year)&(dataset["都道府県名"]==pref),"企業数"].multiply(dataset["労働生産性(千円/人)"]).sum()
        y=dataset.loc[(dataset["集計年"]==year)&(dataset["都道府県名"]==pref),"企業数"].sum()
        z=x/y
        dataset_pref=dataset_pref.append({"集計年":year,"都道府県名":pref,"労働生産性(千円/人)":z},ignore_index=True)
dataset_merge=dataset_pref.append(dataset_jp,ignore_index=True)
max_x=dataset_merge["労働生産性(千円/人)"].max() + 50
fig=px.bar(
    dataset_merge,
    x="労働生産性(千円/人)",
    y="都道府県名",
    color="都道府県名",
    animation_frame="集計年",
    range_x=[0,max_x],
    orientation="h"
)
st.plotly_chart(fig)

    
st.header("■集計年別の労働生産性トップ10")
dataset_pref_top10=pd.DataFrame(columns=["集計年","都道府県名","労働生産性(千円/人)"])
for year in year_list:
    dataset_pref_top10=dataset_pref_top10.append(dataset_pref[(dataset_pref["集計年"]==year)].nlargest(10,"労働生産性(千円/人)"))
option_year=st.selectbox(
    "集計年",
    (year_list) 
)
dataset_pref_top10=dataset_pref_top10[dataset_pref_top10["集計年"]==option_year]
max_x=dataset_pref_top10["労働生産性(千円/人)"].max() + 50
fig=px.bar(
    dataset_pref_top10,
    x="労働生産性(千円/人)",
    y="都道府県名",
    color="都道府県名",
    range_x=[0,max_x],
    orientation="h"
)
st.plotly_chart(fig)

st.text("出典：RESUS（地域経済分析システム）")
st.text("本結果はRESAS（地域経済分析システム）を加工して作成")