import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';

@Injectable({
  providedIn: 'root',
})
export class MessageService {
  messagesMsg: any[] = [];
  docuFlag = 'off';

  constructor(private cookieService: CookieService) {}

  setDocuFlag(value: string) {
    this.docuFlag = value;
  }

  add_msg(message) {
    this.messagesMsg.push(message);
  }

  clear() {
    this.messagesMsg = [];

    const allCookies: {} = this.cookieService.getAll();

    for (const key in allCookies) {
      if (key.startsWith("CANALPROJECT")) {
        this.cookieService.delete(key);
      }
    }
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
