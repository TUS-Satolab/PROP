import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  messages: string[] = [];

  add(message: string) {
    this.messages.push(message);
  }
  clear() {
    this.messages = [];
  }
  clear_info() {
    for ( let i = this.messages.length - 1; i--;) {
      if ( this.messages[i].indexOf('INFO') !== -1) { this.messages.splice(i, 1); }
    }
  }
  constructor() { }
}
