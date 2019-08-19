"""
Purpose: Creates nicely formated latex tables from dataframe. This also breaks 
lines when the maximum number of columns is exceded.
@author: olivergiesecke
"""

def create_table_df(data,name,max_columns=7):
    columnheaders=list(data.columns)
    numbercolumns=len(columnheaders)
    ## Check colum length
    
    if not numbercolumns>max_columns+1:
        #Change made by Anand Chitale: output changed to overleaf_files
        with open("../../output/overleaf_files/"+name+".tex", "w") as f:
            f.write(r"\begin{tabular}{"+"l" + "".join("c" * (numbercolumns-1)) + "}\n")
            f.write("\\hline\\hline \n")
            f.write("\\addlinespace"+" \n")
            f.write(" & ".join([str(x) for x in columnheaders]) + " \\\ \n")    
            f.write("\\hline \n")
            # write data
            for idx,row in data.iterrows():
                # Do formatting for specific tables 
                if row.iloc[0]=="Total":
                    f.write("\\addlinespace"+" \n")
                
                f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")   
        
            f.write("\\hline \n")
            f.write(r"\end{tabular}")

    else:
        aux=(numbercolumns-1)//max_columns
        print("Total number of columns:",numbercolumns)
        if aux==(numbercolumns-1)/max_columns:
            n_tables=aux
        else:
            n_tables=aux+1
            
        print("Split into",n_tables,"tables")
        n_colums=(numbercolumns-1)//n_tables
        print("with",n_colums,"columns each")
        aux_columnheaders=[]
        
        for n_table in range(n_tables):
            aux_c=[columnheaders[0]]
            for column in range(n_colums):
                aux_c.append(columnheaders[(n_table)*n_colums+(column+1)])
             
            aux_columnheaders.append(aux_c)
            
        
        with open("../../output/overleaf_files/"+name+".tex", "w") as f:

            f.write(r"\begin{tabular}{"+"l" + "".join("c" * (n_colums)) + "}\n")
            f.write("\\hline\\hline \n")
            f.write("\\addlinespace"+" \n")
            
            
            for i in range(n_tables):
                aux_table_columns=aux_columnheaders[i]
                data_table=data[aux_table_columns]
            
                f.write(" & ".join([str(x) for x in aux_table_columns]) + " \\\ \n")    
                f.write("\\hline \n")
                # write data
                for idx,row in data_table.iterrows():
                    # Do formatting for specific tables 
                    if row.iloc[0]=="Total":
                        f.write("\\addlinespace"+" \n")
                    
                    f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n") 
                f.write("\\hline \n")
                f.write("\\addlinespace"+" \n")        
            
            f.write(r"\end{tabular}")