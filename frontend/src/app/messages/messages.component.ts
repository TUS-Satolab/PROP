import { Component, OnInit } from '@angular/core';
import { MessageService } from '../message.service';
import {PopoverModule} from 'ngx-smart-popover';
import { CookieService } from 'ngx-cookie-service';



@Component({
  selector: 'app-messages',
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css']
})
export class MessagesComponent implements OnInit {
  private cookieValue: string;
  prevIdArray = [];
  constructor(private cookieService: CookieService, public messageService: MessageService) { }

  ngOnInit() {
    const allCookies: {} = this.cookieService.getAll();
    console.log(allCookies);
    var prevIds = [];
    for (const key in allCookies) {
      const value = allCookies[key];
      prevIds.push(value);
    }
    this.prevIdArray = prevIds;
    const test = this.prevIdArray[0];
  }

  deleteAllCookies() {
    this.cookieService.deleteAll();
  }

  // triggerEvent() {
  //   if (this.prevIdArray) {
  //     return true;
  //   }
  // }

}
