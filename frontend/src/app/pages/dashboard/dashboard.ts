import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ReactiveFormsModule, FormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { MatDividerModule } from '@angular/material/divider';
import { MentorService } from '../../services/mentor.service';
import { BookingService } from '../../services/booking.service';
import { ProfileService } from '../../services/profile.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatListModule,
    MatSelectModule,
    MatDividerModule,
    MatFormFieldModule,
  ],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css'],
  providers: [DatePipe]
})

export class Dashboard implements OnInit {
  profile: any = null;
  saving = false;
  message = '';
  bookings: any[] = [];
  availabilityForm!: FormGroup;
  myAvailability: any[] = [];
  filteredAvailability: any[] = [];
  displayedSlotsForAvailabilityId: number | null = null;
  slotsForShownAvailability: any[] = [];
  selectedDate: string | null = null;
  displayedSlotsDate: string | null = null;
  
  constructor(
    private fb: FormBuilder,
    private mentorService: MentorService,
    private bookingService: BookingService,
    private profileService: ProfileService,
    private auth: AuthService,
    private router: Router,
    private datePipe: DatePipe
  ) {}

  ngOnInit(): void {
    this.availabilityForm = this.fb.group({
      date: [new Date(), Validators.required],
      start_time: ['09:00', Validators.required],
      end_time: ['17:00', Validators.required],
      slot_duration: [30, [Validators.required, Validators.min(5)]]
    });

    this.loadProfile();
    this.loadMyAvailability();
    this.loadMentorBookings();
  }

  // Filter availabilities by selected date
  filterAvailability(): void {
    this.displayedSlotsForAvailabilityId = null
    if (!this.selectedDate) {
      this.filteredAvailability = [...this.myAvailability];
      return;
    }
    const selected = this.datePipe.transform(this.selectedDate, 'yyyy-MM-dd');
    this.filteredAvailability = this.myAvailability.filter(a => a.date === selected);
  }

  // Hide slots panel
  hideSlots(): void {
    this.displayedSlotsForAvailabilityId = null;
    this.slotsForShownAvailability = [];
    this.displayedSlotsDate = null;
  }

  // Add availability
  addAvailability(): void {
    if (this.availabilityForm.invalid) {
      this.message = 'Please fill all fields correctly.';
      return;
    }
    this.saving = true;
    this.message = '';

    const dateVal = this.availabilityForm.value.date as Date;
    const payload = {
      date: this.datePipe.transform(dateVal, 'yyyy-MM-dd'),
      start_time: this.availabilityForm.value.start_time,
      end_time: this.availabilityForm.value.end_time,
      slot_duration: this.availabilityForm.value.slot_duration
    };

    this.mentorService.addAvailability(payload).subscribe({
      next: () => {
        this.saving = false;
        this.message = 'Availability added';
        setTimeout(() => this.message = '', 3000);
        this.availabilityForm.reset({
          date: new Date(),
          start_time: '09:00',
          end_time: '17:00',
          slot_duration: 30
        });
        this.loadMyAvailability();
      },
      error: (err: any) => {
        this.saving = false;
        this.message = err?.error?.detail || 'Failed to add availability';
      }
    });
  }

  // Load all availabilities for mentor
  loadMyAvailability(): void {
    this.mentorService.getMyAvailability().subscribe({
      next: (res: any) => {
        this.myAvailability = res || [];
        this.filterAvailability(); // update filtered list
      },
      error: () => {
        this.myAvailability = [];
        this.filteredAvailability = [];
      }
    });
  }

  // Toggle slots for a particular availability
toggleSlots(avail: any): void {
  if (this.displayedSlotsForAvailabilityId === avail.id) {
    // If already open, close it
    this.displayedSlotsForAvailabilityId = null;
    this.slotsForShownAvailability = [];
  } else {
    // Open this availability only
    this.displayedSlotsForAvailabilityId = avail.id;

    this.mentorService.getSlotsForAvailability(avail.id).subscribe({
      next: (res: any) => this.slotsForShownAvailability = res || [],
      error: () => this.slotsForShownAvailability = []
    });
  }
}
  // Delete availability
  deleteAvailability(availId: number): void {
    if (!confirm('Delete this availability?')) return;

    this.mentorService.deleteAvailability(availId).subscribe({
      next: () => {
        this.message = 'Availability deleted';
        if (this.displayedSlotsForAvailabilityId === availId) this.hideSlots();
        this.loadMyAvailability();
      },
      error: (err: any) => this.message = err?.error?.detail || 'Failed to delete'
    });
  }

  // Load mentor bookings
  loadMentorBookings(): void {
    this.bookingService.getMentorBookings().subscribe({
      next: (res: any) => this.bookings = res || [],
      error: () => this.bookings = []
    });
  }

  // Profile actions
  goToEditProfile(): void { this.router.navigate(['/profile/edit']); }
  signOut(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  loadProfile(): void { 
    this.profileService.getMyProfile().subscribe({ 
      next: (res: any) => this.profile = res, error: () => this.profile = null 
    }); }

    // Delete a single slot
deleteSlot(slotId: number): void {
  if (!confirm('Delete this slot?')) return;

  this.mentorService.deleteSlot(slotId).subscribe({
    next: () => {
      this.message = 'Slot deleted';
      // Remove the deleted slot from the displayed slots
      this.slotsForShownAvailability = this.slotsForShownAvailability.filter(s => s.id !== slotId);
    },
    error: (err: any) => {
      this.message = err?.error?.detail || 'Failed to delete slot';
    }
  });
}

}