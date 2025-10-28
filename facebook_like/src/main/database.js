const sql = require('mssql');

const config = {
  user: 'sa',        // 登录用户名
  password: 'Yunsin@#861123823_shp4',    // 登录密码
  server: 'dbs.kydb.vip',     // 服务器地址
  database: 'FbSocietiesUser',    // 数据库名称
  port: 1433,
  options: {
    encrypt: true,             // 如果是本地连接，设为 false；Azure 需 true
    trustServerCertificate: true, // 本地开发时设 true
    timeout: 30000
  }
}

export async function connectAndQuery() {
  try {
    const pool = await sql.connect(config);

    const result = await pool.request().query('SELECT TOP 10 * FROM FansUser');
    console.log(result.recordset)
  } catch (err) {
    console.log('数据库连接失败：', err);
  }
}

//批量插入集合数据
export async function batchInsertUsers(userMap,SupportInf) {
  try {
    const pool = await sql.connect(config);
    // 开始事务
    const transaction = new sql.Transaction(pool);
    await transaction.begin();

    try {
      for (const [userId, userData] of userMap) {
        const request = new sql.Request(transaction);
        await request
          .input('userid', sql.VarChar(100), userData.userId)
          .input('username', sql.VarChar(100), userData.userName)
          .input('Supportid', sql.VarChar(100), userData.Supportid)
          .query(`INSERT INTO SupportUser_copy1 (userid, username, Supportid)
                  VALUES (@userid, @username, @Supportid) `)
      }
      if (SupportInf != null) {
        //插入单行数据
        const request = new sql.Request(transaction);
        await request
          .input('Supportid', sql.VarChar(100), SupportInf.Supportid)
          .input('SupportName', sql.VarChar(100), SupportInf.title)
          .input('number', SupportInf.SupportCount)
          .query(`INSERT INTO SupportInf_copy1 (Supportid, SupportName, number)
                VALUES (@Supportid, @SupportName, @number) `)
      }
      //提交事务
      await transaction.commit();
      console.log(`成功批量插入 ${userMap.size} 条用户数据`);
    } catch (err) {
      // 回滚事务
      await transaction.rollback();
      console.log('事务回滚', err);
    }

  } catch (err) {
    console.log('批量插入数据失败：', err);
  }
}
