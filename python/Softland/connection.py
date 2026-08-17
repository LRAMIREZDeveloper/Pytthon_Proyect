def connection_sqlserver():
    server = 'sqlreplica01.softlandcloud.cl'
    database = 'TSM1'
    username = 'TSM'
    password = 'Ti0OjW9T9Xn5xVa7w8dXsmm2g0NOyS2W'
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    
    return connection_string