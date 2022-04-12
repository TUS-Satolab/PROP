import { Injectable } from '@angular/core';
import { QUERY_URL, VERSION } from './globals';
import { CookieService } from 'ngx-cookie-service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import * as arrList from './env.json'
const moment = require('moment');


@Injectable({
  providedIn: 'root',
})
export class checkstatus {
  prevIdArray = [];
  constructor(private cookieService: CookieService, private httpClient: HttpClient) {}

  checkStatus() {
    let formStatus = new FormData();
    const headers: HttpHeaders | {} = String(arrList['LOCAL_FLAG']) === '1' ? new HttpHeaders({'Apikey': String(arrList['APIKEY']),}) : {}
    const error_arr = [
      'Error',
      'File format',
      'None',
      'File not aligned',
      'File is not aligned',
      '遺伝的差異計算Error',
      '系統樹作成Error',
      'Check datatype or align definitions',
      'Cancelled',
      'log(0) in Distance Matrix Calculation. Check Type and Genetic Difference',
      'Alignment error',
      'No valid matrix',
      'Time limit of 24 hours reached',
      'Linecount maximum exceeded',
      'Phylogenetic Tree Generation Error',
      'Alignment error',
      'Calculating Genetic Difference Error',
      'Result file is too big'
    ];
    const sec_arr = ['Finished', 'Cancelled'];
    const allCookies: {} = this.cookieService.getAll();
    
    for (const key in allCookies) {
      if (!key.startsWith("CANALPROJECT")) {
        delete allCookies[key]
      }
    }
    // tslint:disable-next-line: forin
    for (const key in allCookies) {
      const value = allCookies[key];
      const valueSplit = value.split(';');
      if (error_arr.includes(valueSplit[0])) {
        // pass
        continue
      } else if (sec_arr.includes(valueSplit[1])) {
        const parsedDate = moment(valueSplit[2], 'YYYY/MM/DD HH:mm');
        if (parsedDate/1000 + 604800 < moment().unix()) {
          this.cookieService.delete(key)
          continue
        }
        continue
        //pass
      } else {
        formStatus.set('result_id', valueSplit[0]);
        formStatus.set('result_kind', 'complete');
        this.httpClient.post(QUERY_URL, formStatus, { headers, observe: 'response'}).subscribe((query) => {
          valueSplit[1] = query.body['msg'];
          valueSplit[0] = query.body['result_id'];
          this.cookieService.set(
            key,
            valueSplit[0] +
              ';' +
              valueSplit[1] +
              ';' +
              valueSplit[2] +
              ';' +
              valueSplit[3] +
              ';' +
              valueSplit[4] +
              ';' +
              String(VERSION), 7,'','',true,"None"
          );
        });
        formStatus.delete('result_id');
        formStatus.delete('result_kind');
      }
    }
  }

  getStatus() {
    const allCookies: {} = this.cookieService.getAll();
    for (const key in allCookies) {
      if (!key.startsWith("CANALPROJECT")) {
        delete allCookies[key]
      }
    }
    
    const prevIds = [];
    // tslint:disable-next-line: forin
    for (var key in allCookies) {
      var value = allCookies[key];
      var valueSplit = value.split(';');

      const date = valueSplit[2];
      const parsedDate = moment(date, 'YYYY/MM/DD HH:mm');
      const parsedDateForList = parsedDate.format('MMM D, YYYY, hh:mm a');
      if (parsedDate/1000 + 604800 < moment().unix()) {
        this.cookieService.delete(key)
        continue
      }

      if (valueSplit[4] === 'align') {
        valueSplit[4] = 'alignm';
      } else if (valueSplit[4] === 'matrix') {
        valueSplit[4] = 'matrix';
      }
      // tslint:disable-next-line: max-line-length
      prevIds.push({
        id: valueSplit[0],
        msg: valueSplit[1],
        time: String(parsedDateForList),
        number: valueSplit[3],
        type: valueSplit[4],
        version: valueSplit[5],
      });
      // tslint:disable-next-line: max-line-length
      // prevIds.push({id: valueSplit[0], msg: valueSplit[1], time: valueSplit[2], number: valueSplit[3], type: valueSplit[4], version: valueSplit[5]});
    }
    this.prevIdArray = prevIds;
    return this.prevIdArray;
  }
}
