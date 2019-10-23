import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { MATRIX_URL } from '../globals';


@Component({
  selector: 'app-matrix',
  templateUrl: './matrix.component.html',
  styleUrls: ['./matrix.component.css']
})
export class MatrixComponent implements OnInit {
  // SERVER_URL = 'http://52.198.155.126:5004/matrix';
  form: FormGroup;

  constructor(public fb: FormBuilder, private httpClient: HttpClient, private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      input_type: [''],
      gapdel: [''],
      model: [''],
      plusgap: [''],
      file: [''],
      task_id: [''],
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
    formData.append('task_id', this.form.get('task_id').value);
    formData.append('input_type', this.form.get('input_type').value);
    formData.append('model', this.form.get('model').value);
    formData.append('gapdel', this.form.get('gapdel').value);
    console.log(this.form.get('plusgap').value);
    if (this.form.get('plusgap').value === true) {
      formData.append('plusgap', this.form.get('plusgap').value);
    }
    // formData.append('plusgap', this.form.get('plusgap').value);
    if ((this.form.get('file').value === '') && (this.form.get('task_id').value === '')) {
      return this.messageService.add_msg('Add either a file or a task ID');
    } else {
      return this.httpClient.post(MATRIX_URL, formData, {observe: 'response' }).subscribe(data => {
        console.log(data);
        var unparsed_id = data.body["task_id"];
        var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        var unparsed_msg = data.body["msg"];
        var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg(parsed_msg);
        this.messageService.add_id(parsed_id);
        });
      }
  }

}
