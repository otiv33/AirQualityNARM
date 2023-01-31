// SQLITE
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');



class Connection {
  db = null;

  async _initDb(){
    this.db = await this._createDbConnection('./db/airQuality.sqlite', (err) => {
      if (err) {
        console.error(err.message);
      }
      console.log('Connected to the airQuality database.');
    });
  }
  _createDbConnection(filename) {
    return open({
        filename,
        driver: sqlite3.Database
    });
  }

  constructor() {
    this._initDb();
  }

  async getMeasurements() {
    try {
      let sql = `SELECT * FROM measurements`;
      const result = await this.db.all(sql)
      // (err,rows) => {
      //   if(err) return cb(err);
      //     return rows;
      // });
      // Sort by id DESC
      return result.sort((a, b) => b.id - a.id);
    } catch (error) {
      console.log(error);
    }
  }

  getTimestamp() {
    var date = new Date(); 
    return date.getFullYear() + "-"+ (date.getMonth()+1) + "-" + date.getDate() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
  }

  insertMeasurement(measurement){
    let sql = `INSERT INTO measurements (pm1,pm25,pm4,pm10,h,t,voc,nox,dateTime) VALUES (?,?,?,?,?,?,?,?,?)`;
    const values = [measurement['pm1'],
                    measurement['pm25'],
                    measurement['pm4'],
                    measurement['pm10'],
                    measurement['h'],
                    measurement['t'],
                    measurement['voc'],
                    measurement['nox'],
                    this.getTimestamp()]
    this.db.run(sql, values);
  }

  closeConnetion(){
    this.db.close();
  }
}
const connection = new Connection();

module.exports = connection;