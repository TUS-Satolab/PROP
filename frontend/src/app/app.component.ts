import { Component, OnInit } from '@angular/core';
// import { MessageService } from './message.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Canal Project';
  scrollTop(event) {
    window.scroll(0, 0);
  }
}
