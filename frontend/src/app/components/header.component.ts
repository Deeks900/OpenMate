import { Component } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {

  constructor(private authService: AuthService, private router: Router) {}

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
}