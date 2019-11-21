import { TestBed } from '@angular/core/testing';

import { CheckstatusService } from './checkstatus.service';

describe('CheckstatusService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CheckstatusService = TestBed.get(CheckstatusService);
    expect(service).toBeTruthy();
  });
});
