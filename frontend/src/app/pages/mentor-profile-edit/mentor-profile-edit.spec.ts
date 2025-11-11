import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MentorProfileEdit } from './mentor-profile-edit';

describe('MentorProfileEdit', () => {
  let component: MentorProfileEdit;
  let fixture: ComponentFixture<MentorProfileEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MentorProfileEdit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MentorProfileEdit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
