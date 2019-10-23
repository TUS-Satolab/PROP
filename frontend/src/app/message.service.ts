import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  messagesMsg: string[] = [];
  messagesId: string[] = [];
  constructor() { }

  add_msg(message: string) {
    this.messagesMsg.push(message);
  }
  add_id(message: string) {
    this.messagesId.push(message);
  }
  clear() {
    this.messagesId = [];
    this.messagesMsg = [];
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
