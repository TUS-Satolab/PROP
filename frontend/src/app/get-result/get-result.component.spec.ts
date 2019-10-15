import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GetResultComponent } from './get-result.component';

describe('GetResultComponent', () => {
  let component: GetResultComponent;
  let fixture: ComponentFixture<GetResultComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GetResultComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GetResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
