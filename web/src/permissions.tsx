/**
 * methods to check permissions in the UI
 * actual permissions should be enforced in the API
 */

import { ServerStatus, UserAccount } from "./api";

function isUserSuper(user: UserAccount | undefined): boolean {
  return user?.tier === 'super'
}

function isUserAdmin(user: UserAccount | undefined): boolean {
  return isUserSuper(user) || user?.tier === 'admin'
}

function isUserVerified(user: UserAccount | undefined): boolean {
  return isUserAdmin(user) || user?.tier === 'verified'
}

export class AuthPermissions {
  readonly user: UserAccount | undefined

  constructor(user: UserAccount | undefined) {
    this.user = user
  }
  
  
  isSuper(): boolean {
    return isUserSuper(this.user)
  }

  isAdmin(): boolean {
    return isUserAdmin(this.user)
  }

  isVerified(): boolean {
    return isUserVerified(this.user)
  }

  canVerifyUser(other: UserAccount): boolean {    
    return this.isAdmin() && other.tier === 'unverified'
  }

  canDeleteUser(other: UserAccount): boolean {
    return this.isSuper() && this.user?.id !== other.id
  }

  canResetPassword(other: UserAccount): boolean {

    return this.isSuper() || !isUserAdmin(other)
  }

  canMakeAdmin(other: UserAccount): boolean {
    return this.isSuper() && other.tier === 'verified'
  }
  
  canRemoveAdmin(other: UserAccount): boolean {
    return this.isSuper() && other.tier === 'admin'
  }

  canDeleteServer(server: ServerStatus): boolean {
    return this.isSuper()
  }

}


// interface Permissions {
//   canVerifyUser: (other: User) => boolean
//   canDeleteUser: (other: User) => boolean
//   canResetPassword: (other: User) => boolean
//   canMakeAdmin: (other: User) => boolean
//   canRemoveAdmin: (other: User) => boolean
// }

export function getPermissions(user: UserAccount | undefined): AuthPermissions {
  return new AuthPermissions(user);
}