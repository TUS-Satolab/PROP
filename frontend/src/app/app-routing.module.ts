import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AlignComponent } from './align/align.component';
import { CompleteCalcComponent } from './complete-calc/complete-calc.component';
import { MatrixComponent } from './matrix/matrix.component';
import { TreeComponent } from './tree/tree.component';
import { MessagesComponent } from './messages/messages.component';
import { DocumentationComponent } from './documentation/documentation.component';

const routes: Routes = [
  { path: '', redirectTo: 'complete', pathMatch: 'full' },
  { path: 'align', component: AlignComponent },
  { path: 'complete', component: CompleteCalcComponent },
  { path: 'matrix', component: MatrixComponent },
  { path: 'tree', component: TreeComponent },
  { path: 'messages', component: MessagesComponent },
  { path: 'documentation', component: DocumentationComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
