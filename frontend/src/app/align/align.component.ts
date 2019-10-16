import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';

@Component({
  selector: 'app-align',
  templateUrl: './align.component.html',
  styleUrls: ['./align.component.css']
})
export class AlignComponent implements OnInit {
  SERVER_URL = 'http://localhost:5004/alignment';
  form: FormGroup;

  constructor(public fb: FormBuilder, private httpClient: HttpClient, private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      file: [''],
      align_clw_opt: [''],
      align_method: [''],
      input_type: [''],
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
    let res: [''];

    const httpOptions: { headers; observe; } = {
      headers: new HttpHeaders({
        'Content-Type':  'text/plain'
      }),
      observe: 'response'
    };

    formData.append('align_clw_opt', this.form.get('align_clw_opt').value);
    formData.append('file', this.form.get('file').value);
    formData.append('input_type', this.form.get('input_type').value);
    formData.append('align_method', this.form.get('align_method').value);
    // return this.httpClient.post(this.SERVER_URL, formData).subscribe(data => {
    //   console.log(data);
    // });
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
    // this.httpClient.post(this.SERVER_URL, formData).subscribe(
    //   (res) => console.log(res),
    //   (err) => console.log(err)
    // );
    this.messageService.add('Test');
  }


}
