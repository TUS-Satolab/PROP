import { Component, OnInit } from '@angular/core';
import {formatDate} from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { TREE_URL } from '../globals';
import { CookieService } from 'ngx-cookie-service';


@Component({
  selector: 'app-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.css']
})
export class TreeComponent implements OnInit {
  // SERVER_URL = 'http://52.198.155.126:5004/tree';
  form: FormGroup;
  filename = "";


  constructor(private cookieService: CookieService, public fb: FormBuilder, private httpClient: HttpClient, 
              private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      tree: ['nj', Validators.required],
      file: ['', Validators.required],
      task_id: [''],
    });
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      const file = event.target.files[0];
      this.form.get('file').setValue(file);
      this.filename = file.name;
    }
  }

  reset() {
    this.form.reset();
  }

  onSubmit() {
    const formData: any = new FormData();
    const dateTime = formatDate(new Date(), 'yyyy/MM/dd HH:mm', 'en');
    formData.append('tree', this.form.get('tree').value);
    formData.append('file', this.form.get('file').value);
    formData.append('task_id', this.form.get('task_id').value);
    if ((this.form.get('file').value === '') && (this.form.get('task_id').value === '')) {
      return this.messageService.add_msg('Add either a file or a task ID');
    } else {
      return this.httpClient.post(TREE_URL, formData, {observe: 'response' }).subscribe(data => {
        var unparsed_id = data.body["task_id"];
        var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        var unparsed_msg = data.body["msg"];
        var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg({id: parsed_id, msg: parsed_msg, time: dateTime});
        const allCookies: {} = this.cookieService.getAll();
        let i = Object.keys(allCookies).length + 1;
        // console.log(i);
        if (parsed_id !== 'None') {
          // this.cookieService.set(String ( i ), parsed_id);
          this.cookieService.set(String ( i ), parsed_id + ';' + parsed_msg + ';' + dateTime + ';' + i + ';' + 'tree');
        }
        });
      }
  }

}
