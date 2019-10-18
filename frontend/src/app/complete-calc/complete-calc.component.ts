import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';

@Component({
  selector: 'app-complete-calc',
  templateUrl: './complete-calc.component.html',
  styleUrls: ['./complete-calc.component.css']
})
export class CompleteCalcComponent implements OnInit {
  SERVER_URL = 'http://52.198.155.126:5004/complete';
  form: FormGroup;

  constructor(public fb: FormBuilder, private httpClient: HttpClient, private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      file: [''],
      align_method: ['none'],
      input_type: ['none'],
      gapdel: ['none'],
      model: ['none'],
      plusgap: [''],
      tree: ['none'],
      align_clw_opt: [''],
    });
  }

  reset() {
    this.form.reset();
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      const file = event.target.files[0];
      this.form.get('file').setValue(file);
    }
  }
  onSubmit() {
    const formData: any = new FormData();
    formData.append('file', this.form.get('file').value);
    formData.append('align_method', this.form.get('align_method').value);
    formData.append('input_type', this.form.get('input_type').value);
    formData.append('gapdel', this.form.get('gapdel').value);
    formData.append('model', this.form.get('model').value);
    console.log(this.form.get('plusgap').value);
    if (this.form.get('plusgap').value === true) {
      formData.append('plusgap', this.form.get('plusgap').value);
    }
    formData.append('tree', this.form.get('tree').value);
    formData.append('align_clw_opt', this.form.get('align_clw_opt').value);

    return this.httpClient.post(this.SERVER_URL, formData, {
      observe: 'response'
    }).subscribe(data => {
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
