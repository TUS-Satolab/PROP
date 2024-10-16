import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AlignComponent } from './align/align.component';
import { CompleteCalcComponent } from './complete-calc/complete-calc.component';
import { MatrixComponent } from './matrix/matrix.component';
import { TreeComponent } from './tree/tree.component';
import { MessagesComponent } from './messages/messages.component';
import { DocumentationComponent } from './documentation/documentation.component';
import { strict as assert } from 'assert';
import * as arrList from './env.json'

assert(String(arrList['LOCAL_FLAG'].length !== 0), 'FILE_SIZE_LIMIT is not defined')
assert(String(arrList['APIKEY'].length !== 0), 'FILE_SIZE_LIMIT is not defined')
assert(Number(arrList['FILE_SIZE_LIMIT']) > 0, 'FILE_SIZE_LIMIT is not defined')

const routes: Routes = [
  { path: '', redirectTo: 'complete', pathMatch: 'full' },
  { path: 'align', component: AlignComponent },
  { path: 'complete', component: CompleteCalcComponent },
  { path: 'matrix', component: MatrixComponent },
  { path: 'tree', component: TreeComponent },
  { path: 'messages', component: MessagesComponent },
  { path: 'instructions', component: DocumentationComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    useHash: true, //add
  })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
