import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MenteeHome } from './mentee-home';

describe('MenteeHome', () => {
  let component: MenteeHome;
  let fixture: ComponentFixture<MenteeHome>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MenteeHome]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MenteeHome);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
