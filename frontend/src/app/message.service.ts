import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class MessageService {
  messagesMsg: any[] = [];
  docuFlag = 'off';
  // messagesId: string[] = [];
  // messagesDate: string[] = [];
  constructor(private cookieService: CookieService) { }

  setDocuFlag(value: string) {
    this.docuFlag = value;
  }

  add_msg(message) {
    this.messagesMsg.push(message);
  }
  // add_id(message: string) {
  //   this.messagesId.push(message);
  // }
  // add_date(message: string) {
  //   this.messagesDate.push(message);
  // }
  clear() {
    // this.messagesId = [];
    this.messagesMsg = [];
    this.cookieService.deleteAll();
    location.reload();
  }
  clear_info() {
    this.messagesMsg = [];
  }

  /* To copy any Text */
  copyText(val: string) {
    const selBox = document.createElement('textarea');
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    selBox.value = val;
    document.body.appendChild(selBox);
    selBox.focus();
    selBox.select();
    document.execCommand('copy');
    document.body.removeChild(selBox);
  }
}
