import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MessageService } from '../message.service';
import { CookieService } from 'ngx-cookie-service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { GET_RESULT_URL, QUERY_URL, CANCEL_URL, VERSION } from '../globals';
import { environment } from '../../environments/environment';
import { saveAs } from 'file-saver';
import { checkstatus } from '../checkstatus.service';
import * as d3 from 'd3';
import * as svg_download from 'save-svg-as-png';
import { Router } from '@angular/router';
const JSZip = require('jszip');
import { Tree, FigTree, rectangularLayout, branch, circle, tipLabel, internalNodeLabel } from 'figtree/dist/figtree.cjs.min';

@Component({
  selector: 'app-messages',
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css'],
})
export class MessagesComponent implements AfterViewInit {
  horizontalMultiplier = 900
  verticalMultiplier = 900
  svgWidth  = 900;
  svgHeight = 900;
  horizontalScale(event:any) {
    this.horizontalMultiplier = event.target.value
  }
  verticalScale(event:any) {
    this.verticalMultiplier = event.target.value
  }


  branchSettings: any;
  figTree: FigTree;

  fillFlag = false;

  @ViewChild('svg123', { static: false }) treeSvg: ElementRef;

  private cookieValue: string;
  prevIdArray = [];
  showButton = false;
  widthSVG = 1000;
  heightSVG = 1000;
  delay = (ms) => new Promise((res) => setTimeout(res, ms));
  form: FormGroup;
  tree: any;
  data: any;
  linearFlag: boolean;
  downloadFlag = 0;
  activateFlag = 0;
  treeActiveFlag = false;

  // tslint:disable-next-line: max-line-length
  constructor(
    private _checkstatus: checkstatus,
    private httpClient: HttpClient,
    private cookieService: CookieService,
    public messageService: MessageService,
    private router: Router
  ) {}
  ngAfterViewInit(): void {
  }
  ngOnInit() {
    const allCookies: {} = this.cookieService.getAll();
    for (const key in allCookies) {
      if (!key.startsWith("CANALPROJECT")) {
        delete allCookies[key]
      }
    }
    for (let key in allCookies) {
      const valueSplit = allCookies[key].split(';')
      if (valueSplit.length < 6) {
        this.cookieService.delete(key);
      } else if (Number(valueSplit[5]) !== VERSION) {
        this.cookieService.delete(key);
      }
    }

    this.prevIdArray = this._checkstatus.getStatus();
    setInterval(() => {
      this._checkstatus.checkStatus();
      this.prevIdArray = this._checkstatus.getStatus();
    }, 3000);
  }

  async downloadFiles(input) {
    const headers: HttpHeaders = new HttpHeaders({'Apikey': environment.apiKey});
    const formData: any = new FormData();
    formData.set('result_id', input);
    formData.set('result_kind', 'complete');
    this.downloadFlag = 1;
    this.activateFlag = input;
    const query = await this.httpClient.post(QUERY_URL, formData, { headers, observe: 'response' }).toPromise()
      if (query.body['msg'] === 'Finished') {
        const data = await this.httpClient.post(GET_RESULT_URL, formData, { headers, responseType: 'arraybuffer' }).toPromise()
          const blob = new Blob([data], {
            type: 'application/zip',
          });
          const jszip = new JSZip();
          let result: any;
          await jszip.loadAsync(blob).then(async (zip) => {
            try {
              if (this.figTree === undefined ) {
                result = await this.showTree(input);
              }
              while (this.treeActiveFlag === false) {
                console.log("waiting for showTree to finish, sleep 1 sec")
                  await this.delay(1000);
              }
              if (result !== "ERROR") {
                while (!this.figTree || this.figTree.scales.width === 0 || this.figTree.scales.height === 0) {
                  console.log("sleep 1 sec")
                  await this.delay(1000);
                }
                const svg = this.treeSvg.nativeElement;
                const canvas = document.createElement("canvas");
                canvas.width = svg.width.baseVal.value;
                canvas.height = svg.height.baseVal.value;
                await svg_download.svgAsPngUri(svg, {modifyCss: (selector, properties) => {
                  if (selector.startsWith('.internal-node') || selector.startsWith('.external-node')) {
                    properties = 'opacity: 0;'
                  } else {
                    properties = ''
                  }
                  return selector + '{' + properties + '}';
                }}, (uri: any) => {
                  const output = this.dataURItoBlob(uri);
                  zip.file('figtree.png', output);
                });
              }
            } catch (e) {
              console.log("ERROR\n", e)
              zip.remove('figtree.png');
            }
            zip.generateAsync({ type: 'blob' }).then(async function (content) {
              await saveAs(content, 'results.zip');
            });
          });
          this.downloadFlag = 0;
          this.activateFlag = 0;
      }

  }

  // deleteAllCookies() {
  //   this.cookieService.deleteAll();
  // }

  async downloadTree() {
    const svg = this.treeSvg.nativeElement;
    await svg_download.svgAsPngUri(svg, {modifyCss: (selector, properties) => {

      if (selector.startsWith('.internal-node') || selector.startsWith('.external-node')) {
        properties = 'opacity: 0;'
      } else {
        properties = ''
      }
      return selector + '{' + properties + '}';
    }}, async (uri: any) => {
      const output = this.dataURItoBlob(uri);
      await saveAs(output, 'figtree.png');
    });
  }

  dataURItoBlob(dataURI) {
    // convert base64 to raw binary data held in a string
    // doesn't handle URLEncoded DataURIs - see SO answer #6850276 for code that does this
    var byteString = atob(dataURI.split(',')[1]);
    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    // write the bytes of the string to an ArrayBuffer
    var ab = new ArrayBuffer(byteString.length);
    // create a view into the buffer
    var ia = new Uint8Array(ab);
    // set the bytes of the buffer to the correct values
    for (var i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    // write the ArrayBuffer to a blob, and you're done
    var blob = new Blob([ab], { type: mimeString });
    return blob;
  }
  notfinished(input): boolean {
    if (input !== 'Finished') {
      return true;
    }
  }

  started(input): boolean {
    const array = ['Running.', 'Running..', 'Finished'];
    if (array.includes(input)) {
      return true;
    } else {
      return false;
    }
  }

  cancelJob(input) {
    const headers: HttpHeaders = new HttpHeaders({'Apikey': environment.apiKey});
    const formData: any = new FormData();
    formData.append('result_id', input);
    const allCookies: {} = this.cookieService.getAll();

    for (const key in allCookies) {
      if (!key.startsWith("CANALPROJECT")) {
        delete allCookies[key]
      }
    }

    this.httpClient.post(CANCEL_URL, formData, { headers, observe: 'response' }).subscribe((query) => {
      // tslint:disable-next-line: forin
      for (let key in allCookies) {
        let value = allCookies[key];
        let valueSplit = value.split(';');
        if (valueSplit[0] === input) {
          console.log(input);
          valueSplit[1] = query.body['msg'];
          this.cookieService.set(
            key,
            valueSplit[0] +
              ';' +
              valueSplit[1] +
              ';' +
              valueSplit[2] +
              ';' +
              valueSplit[3] +
              ';' +
              valueSplit[4] +
              ';' +
              valueSplit[5],
              7,'','',true,"None"
          );
        }
      }
    });
  }

  async showTree(input): Promise<string> {
    try {
      if (!!this.figTree && !!this.figTree.scales && (this.figTree.scales.width !== 0 || this.figTree.scales.height !== 0)) {
        const result = await this.deleteTree();
      }
      this.showButton = true;
      const headers: HttpHeaders = new HttpHeaders({'Apikey': environment.apiKey});

      const formData: any = new FormData();

      formData.append('result_id', input);
      formData.append('result_kind', 'tree');
      const query = await this.httpClient.post(QUERY_URL, formData, { headers, observe: 'response' }).toPromise()
      if (query.body['msg'] === 'Finished') {
        const data = await this.httpClient.post(GET_RESULT_URL, formData, { headers, responseType: 'text' }).toPromise()
          if (data === 'Tree file not found. Run the calculation first.') {
            await this.deleteTree()
            this.treeActiveFlag = true;
            return "ERROR"
          }
          const tree = await Tree.parseNewick(data);
          const layout = rectangularLayout;
          const margins = { top: 10, bottom: 60, left: 10, right: 400 };
          this.branchSettings = branch().hilightOnHover().reRootOnClick().curve(d3.curveStepBefore);

          this.figTree = await new FigTree(this.treeSvg.nativeElement, margins, tree, { width: this.svgWidth, height: this.svgHeight })
                      .layout(rectangularLayout)
                      .nodes(
                      circle()
                          .attr("r",5)
                          .hilightOnHover(10)
                          .rotateOnClick(),
                          tipLabel(d=>d.name),
                          internalNodeLabel(d=>{d.label})

                      )
                      .nodeBackgrounds(
                          circle()
                              .attr("r",7)
                      )
                      .branches(this.branchSettings);
          layout.internalNodeLabels="probability";
          this.figTree.settings.width = this.horizontalMultiplier;
          this.figTree.settings.height = this.verticalMultiplier;
          this.figTree.update();
          this.linearFlag = true;
          this.treeActiveFlag = true;
          return "DONE"
      } else {
        this.treeActiveFlag = true;
        return "ERROR"
      }
    } catch(e) {
      console.log("Error in showTree\n", e)
      return "ERROR"
    }
  }

  async deleteTree(): Promise<string> {
    d3.select(this.treeSvg.nativeElement).selectAll("*").remove();
    this.figTree = undefined
    this.showButton = false
    return 'Done'
  }

  applySize() {
    this.svgHeight = this.verticalMultiplier;
    this.figTree.settings.height = this.svgHeight;
    this.svgWidth = this.horizontalMultiplier;
    this.figTree.settings.width = this.svgWidth;
    this.figTree.update();
  }

  async clear_history(){
	this.messageService.clear();
  }

}
