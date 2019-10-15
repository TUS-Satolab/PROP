import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';

@Component({
  selector: 'app-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.css']
})
export class TreeComponent implements OnInit {
  SERVER_URL = 'http://localhost:5004/tree';
  form: FormGroup;

  constructor(public fb: FormBuilder, private httpClient: HttpClient, private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      tree: [''],
      file: [''],
      task_id: [''],
    });
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      const file = event.target.files[0];
      this.form.get('file').setValue(file);
    }
  }

  onSubmit() {
    const formData: any = new FormData();
    formData.append('tree', this.form.get('tree').value);
    formData.append('file', this.form.get('file').value);
    formData.append('task_id', this.form.get('task_id').value);
    if ((this.form.get('file').value === '') && (this.form.get('task_id').value === '')) {
      return this.messageService.add('Add either a file or a task ID');
    } else {
      return this.httpClient.post(this.SERVER_URL, formData, {observe: 'response' }).subscribe(data => {
        console.log(data);
        var unparsed_id = data.body["task_id"];
        var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        var unparsed_msg = data.body["msg"];
        var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add(parsed_msg);
        this.messageService.add(parsed_id);
        });
      }
  }

}
