def fetch_json_to_df():
    publication = pd.DataFrame()
    for i in range(6):
        tmp_ = pd.read_json('publications_{0}.json'.format(i+1))
        publication = pd.concat([publication, tmp_])
    return pd.DataFrame(list(publication['items']))

def honey_cluster(df): 
    publication_product = fetch_json_to_df()
    
    if len(df['location'].str.split("/")) > 3:
        df['landing_page'] = df['location'].str.split("/").str[3]
    else: 
        df['landing_page'] = "home"
    
    #product_view와 payments 2개의 dataframe 으로 나누기
    product_view = df[df['landing_page'] == "product"]
    payments = df[df['landing_page'] == "payment"]
    payments_process = payments[payments['location'].str.contains('process')]
    #url 발라내기 
    payments_process['offering_type'] = 0
    
    payments_process['code'] = [re.split("[/?=&]", x)[6] for x in list(payments_process.location)]
    payments_process['offering_type'] = [re.split("[/?&=]",each[each.find("pt="):])[1] for each in list(payments_process.location)]
    for x in list(product_view.location):
        if len(re.split("[/?=&]", x)) > 6:
            product_view['code'] = re.split("[/?=&]", x)[6]
        elif len(re.split("[/?=&]", x)) > 4:
            product_view['code'] = re.split("[/?=&]", x)[4]
        else:
            product_view["code"] = None

    
    #payments_process에서 sell만 남기고 id count df로 만들기 
    payments_process_ = payments_process[payments_process['offering_type'] =="SELL"]
    product_purchase_count = pd.DataFrame(payments_process['code'].value_counts())
    product_purchase_count = product_purchase_count.reset_index()
    product_purchase_count.columns = ['id', 'purchase_cnt']
    
    #product view에서 code count df로 만들기 
    product_view_count = pd.DataFrame(product_view['code'].value_counts())
    product_view_count = product_view_count.reset_index()
    product_view_count.columns = ['code', 'view_cnt']
    
    #payments 와 product table과 merge 시키기 
    products_for_map = publication_product[['id', 'code','title']]
    product_payment_count_merge = pd.merge(product_purchase_count,products_for_map,how='inner', on='id')

    #product view와 product table merge 시키기
    product_view_count_merge = pd.merge(product_view_count,products_for_map,how='inner', on='code')

    #product_view & payments left join
    publication_conv_df = pd.merge(product_payment_count_merge,product_view_count_merge, how='inner', on='code')
    publication_conv_df.drop(['id_y'],axis = 1, inplace = True )
    publication_conv_df['conversion'] = publication_conv_df['purchase_cnt'] / publication_conv_df['view_cnt'] *100
    
    #honey cluster는 conversion rate 가 (평균 + 표준편차)이상 이면서 view count는 중간값 이하인 products 군집
    conversion = publication_conv['conversion']
    views = publication_conv['view_cnt']
    honey_cluster = publication_conv[(conversion > np.quantile(conversion, .75))
                 & (views < np.median(views))]
    
    #honey cluster에 해당하는 product id를 list로 저장
    honey_clsuter_id = honey_cluster['code'].unique()
    
    
    return honey_clsuter_id
    
    
    
    
