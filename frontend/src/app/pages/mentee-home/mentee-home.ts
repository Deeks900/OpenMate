import { Component, OnInit } from '@angular/core';
import { MentorService } from '../../services/mentor.service';
import { QuoteService } from '../../services/quote.service';
import { MenteeService } from '../../services/mentee.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';


@Component({
  selector: 'app-mentee-home',
  imports: [CommonModule, FormsModule, HttpClientModule, MatSnackBarModule, MatButtonModule],
  templateUrl: './mentee-home.html',
  styleUrl: './mentee-home.css',
})
export class MenteeHome {
  mentors: any[] = [];
  filteredMentors: any[] = [];
  searchText:string = "";
  quoteText = '';
  quoteAuthor = '';
  quoteLoaded: boolean = false;

  selectedMentor: any = null;
  selectedSlot: string = "";
  mentorSlots: string[] = [];
  selectedDate: string = "";
  videoLink: string = "";
  minDate: string = '';
  noSlots: boolean = false; 

  isBooking: boolean = false;

  menteeBookings: any[] = [];
  bookingsLoaded: boolean = false;

  greetingMessage: string = "";
  userName: string = "";

  
  constructor(private mentorService: MentorService,  private authService: AuthService, private quoteService: QuoteService, private menteeService: MenteeService, private snack: MatSnackBar, private router: Router) {}

  ngOnInit() {
    this.loadUser();
    this.loadMentors();
    this.loadQuote();
    this.loadMenteeBookings();
    // Set minDate to today (local date)
    const today = new Date();
    this.minDate = today.getFullYear() + '-' +
                   String(today.getMonth() + 1).padStart(2, '0') + '-' +
                   String(today.getDate()).padStart(2, '0');

    // Optionally, initialize selectedDate to today
    this.selectedDate = this.minDate;
  }

  loadUser() {
    this.authService.getCurrentUser().subscribe({
      next: (user: any) => {
        this.userName = user.name;  // adjust according to your API response
        this.setGreeting();
      },
      error: () => {
        this.userName = "User";  // fallback
        this.setGreeting();
      }
    });
  }

  setGreeting() {
    const hour = new Date().getHours();
    let greeting = "";

    if (hour < 12) {
      greeting = "Good morning";
    } else if (hour < 18) {
      greeting = "Good afternoon";
    } else {
      greeting = "Good evening";
    }

    this.greetingMessage = `${greeting}, ${this.userName}!`;
  }

  loadMentors() {
    this.mentorService.getAllMentors().subscribe((res: any) => {
      this.mentors = res;
      this.filteredMentors = res;
      console.log(this.filteredMentors)
    });
  }


  

  loadQuote() {
    this.quoteService.getQuote().subscribe((data) => {
      console.log(data)
      this.quoteText = data.quote;
      this.quoteAuthor = data.author;
      this.quoteLoaded = true; 
    });
  }

  loadMenteeBookings() {
  this.menteeService.getMenteeBookings().subscribe((res: any) => {
    this.menteeBookings = res;
    this.bookingsLoaded = true;
  });
}

openLink(url: string) {
  window.open(url, "_blank");
}


  filterMentors() {
    const txt = this.searchText.toLowerCase();
    console.log(txt)

    this.filteredMentors = this.mentors.filter(m =>
      m.user_name.toLowerCase().includes(txt) ||
      m.expertise.toLowerCase().includes(txt)
    );
  }

 

// Triggered when user selects a date
 onDateChange() {
    if (!this.selectedMentor || !this.selectedDate) return;

    this.mentorService.getSlots(this.selectedMentor.user_id, this.selectedDate)
      .subscribe(slots => {
        if (!slots || slots.length === 0) {
          this.mentorSlots = [];
          this.noSlots = true;
        } else {
          this.mentorSlots = slots;
          this.noSlots = false;
        }
        this.selectedSlot = "";
      });
  }

  openBookingCard(mentor: any) {
  this.selectedMentor = mentor;
  this.selectedSlot = '';
  this.selectedDate = '';
  this.mentorSlots = [];
  this.noSlots = false;
  } 

  signOut() {
    this.authService.logout().subscribe({
      next: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        this.router.navigate(['/login']);
      },
      error: () => {
        // Even if backend logout fails → clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        this.router.navigate(['/login']);
      }
    });
  }


confirmBooking(){
  if (!this.selectedMentor || !this.selectedSlot) {
    return;
  }

  this.isBooking = true; 

  const payload = {
    mentor_id: this.selectedMentor.id,
    slot: this.selectedSlot,  // e.g. "10:00 - 10:30"
    date: this.selectedDate
  };
   
  this.mentorService.bookSlot(payload).subscribe({
    next: (res: any) => {
      this.snack.open("Booking confirmed!", "Close", {
    duration: 2500,
    panelClass: ["glass-snackbar", "success-snackbar"]
  });

      // Reset UI
      this.isBooking = false;
      this.selectedSlot = "";
      this.selectedMentor = null;
      this.mentorSlots = [];

      // 2. Immediately refresh upcoming bookings
    this.loadMenteeBookings()
    },
    error: (err) => {
      console.error(err);
      this.snack.open("Booking Failed!", "Close", {
    duration: 2500,
    panelClass: ["glass-snackbar", "error-snackbar"]
  });
  this.isBooking = false;
    }
  });


}


}
