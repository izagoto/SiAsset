# Flow Diagram Aplikasi Cyber Asset Management

## 1. Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Auth API
    participant Auth Service
    participant Database
    participant JWT

    Client->>Auth API: POST /api/v1/auth/login<br/>{email, password}
    Auth API->>Auth Service: authenticate_user(email, password)
    Auth Service->>Database: Query user by email
    Database-->>Auth Service: User data
    Auth Service->>Auth Service: Verify password
    alt Password Valid & User Active
        Auth Service->>JWT: Create access_token & refresh_token
        JWT-->>Auth Service: Tokens
        Auth Service-->>Auth API: {access_token, refresh_token}
        Auth API-->>Client: 200 OK<br/>{status, message, data: {tokens}}
    else Invalid Credentials
        Auth Service-->>Auth API: InvalidCredentialsException
        Auth API-->>Client: 401 Unauthorized
    else User Inactive
        Auth Service-->>Auth API: InactiveUserException
        Auth API-->>Client: 403 Forbidden
    end
```

## 2. Authorization Flow (RBAC)

```mermaid
flowchart TD
    Start([Request dengan Token]) --> ValidateToken{Validate JWT Token}
    ValidateToken -->|Invalid| Error401[401 Unauthorized]
    ValidateToken -->|Valid| GetUser[Get User dari Database]
    GetUser --> LoadRole[Load User Role]
    LoadRole --> CheckPermission{Check Permission}
    
    CheckPermission -->|Has Permission| Allow[Allow Access]
    CheckPermission -->|No Permission| Error403[403 Forbidden]
    
    Allow --> Execute[Execute Endpoint]
    Execute --> Success[200 OK Response]
    
    Error401 --> End([End])
    Error403 --> End
    Success --> End
    
    style ValidateToken fill:#ffeb3b
    style CheckPermission fill:#ff9800
    style Allow fill:#4caf50
    style Error401 fill:#f44336
    style Error403 fill:#f44336
```

## 3. Asset Management Flow

```mermaid
flowchart TD
    Start([User Request]) --> CheckAuth{Authenticated?}
    CheckAuth -->|No| AuthError[401 Unauthorized]
    CheckAuth -->|Yes| CheckPermission{Has MANAGE_ASSETS<br/>Permission?}
    
    CheckPermission -->|No| PermissionError[403 Forbidden]
    CheckPermission -->|Yes| Action{Action Type}
    
    Action -->|Create| CreateFlow[Create Asset Flow]
    Action -->|Read| ReadFlow[List/Get Asset Flow]
    Action -->|Update| UpdateFlow[Update Asset Flow]
    Action -->|Delete| DeleteFlow[Delete Asset Flow]
    
    CreateFlow --> ValidateCreate[Validate Asset Data]
    ValidateCreate -->|Invalid| ValidationError[422 Validation Error]
    ValidateCreate -->|Valid| CheckUnique{Check Asset Code<br/>& Serial Number<br/>Uniqueness}
    CheckUnique -->|Duplicate| DuplicateError[422: Code/Serial Exists]
    CheckUnique -->|Unique| CreateDB[Create in Database]
    CreateDB --> AuditLog1[Log to Audit]
    AuditLog1 --> Success1[201 Created]
    
    ReadFlow --> QueryDB[Query Assets from DB]
    QueryDB --> CheckEmpty{Data Empty?}
    CheckEmpty -->|Yes| NotFound[404 Not Found]
    CheckEmpty -->|No| Success2[200 OK with Data]
    
    UpdateFlow --> GetAsset[Get Asset by ID]
    GetAsset -->|Not Found| NotFound
    GetAsset -->|Found| ValidateUpdate[Validate Update Data]
    ValidateUpdate --> UpdateDB[Update in Database]
    UpdateDB --> AuditLog2[Log to Audit]
    AuditLog2 --> Success3[200 OK]
    
    DeleteFlow --> GetAsset2[Get Asset by ID]
    GetAsset2 -->|Not Found| NotFound
    GetAsset2 -->|Found| DeleteDB[Delete from Database]
    DeleteDB --> AuditLog3[Log to Audit]
    AuditLog3 --> Success4[200 OK]
    
    AuthError --> End([End])
    PermissionError --> End
    ValidationError --> End
    DuplicateError --> End
    NotFound --> End
    Success1 --> End
    Success2 --> End
    Success3 --> End
    Success4 --> End
    
    style CheckAuth fill:#ffeb3b
    style CheckPermission fill:#ff9800
    style CreateFlow fill:#2196f3
    style ReadFlow fill:#2196f3
    style UpdateFlow fill:#2196f3
    style DeleteFlow fill:#2196f3
    style Success1 fill:#4caf50
    style Success2 fill:#4caf50
    style Success3 fill:#4caf50
    style Success4 fill:#4caf50
    style AuthError fill:#f44336
    style PermissionError fill:#f44336
    style ValidationError fill:#f44336
    style DuplicateError fill:#f44336
    style NotFound fill:#f44336
```

## 4. Loan Management Flow (Status Transition)

```mermaid
stateDiagram-v2
    [*] --> PENDING: User Creates Loan Request
    
    PENDING --> APPROVED: Super Admin Approves
    PENDING --> REJECTED: Super Admin Rejects
    
    APPROVED --> BORROWED: User Starts Borrowing
    APPROVED --> REJECTED: Super Admin Rejects (before borrowing)
    
    BORROWED --> RETURNED: User/Admin Returns Asset
    BORROWED --> OVERDUE: Due Date Passed (Auto)
    
    OVERDUE --> RETURNED: User/Admin Returns Asset
    
    REJECTED --> [*]
    RETURNED --> [*]
    
    note right of PENDING
        Initial state when
        loan request created
    end note
    
    note right of APPROVED
        Loan approved by
        Super Admin
    end note
    
    note right of BORROWED
        Asset is currently
        being used
    end note
    
    note right of OVERDUE
        Automatic status when
        due_date passed
    end note
    
    note right of RETURNED
        Asset has been
        returned
    end note
```

## 5. Loan Request Flow (Detailed)

```mermaid
flowchart TD
    Start([User Creates Loan Request]) --> CheckAuth{Authenticated?}
    CheckAuth -->|No| AuthError[401 Unauthorized]
    CheckAuth -->|Yes| CheckPermission{Has CREATE_LOAN<br/>Permission?}
    
    CheckPermission -->|No| PermissionError[403 Forbidden]
    CheckPermission -->|Yes| ValidateData[Validate Loan Data]
    
    ValidateData -->|Invalid| ValidationError[422 Validation Error]
    ValidateData -->|Valid| CheckAsset[Get Asset by ID]
    
    CheckAsset -->|Not Found| AssetNotFound[404 Asset Not Found]
    CheckAsset -->|Found| CheckAssetStatus{Asset Status<br/>Available?}
    
    CheckAssetStatus -->|Not Available| AssetNotAvailable[422: Asset Not Available]
    CheckAssetStatus -->|Available| CreateLoan[Create Loan with Status PENDING]
    
    CreateLoan --> UpdateAssetStatus[Update Asset Status]
    UpdateAssetStatus --> AuditLog[Log to Audit]
    AuditLog --> Success[201 Created<br/>Loan Status: PENDING]
    
    AuthError --> End([End])
    PermissionError --> End
    ValidationError --> End
    AssetNotFound --> End
    AssetNotAvailable --> End
    Success --> End
    
    style CheckAuth fill:#ffeb3b
    style CheckPermission fill:#ff9800
    style CheckAssetStatus fill:#ff9800
    style Success fill:#4caf50
    style AuthError fill:#f44336
    style PermissionError fill:#f44336
    style ValidationError fill:#f44336
    style AssetNotFound fill:#f44336
    style AssetNotAvailable fill:#f44336
```

## 6. Loan Approval/Rejection Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Service
    participant Validator
    participant Database
    participant Audit

    User->>API: POST /loans/{id}/approve<br/>(Super Admin Only)
    API->>Service: approve_loan(loan_id, approver_id)
    Service->>Database: Get Loan by ID
    Database-->>Service: Loan Data
    
    Service->>Validator: Validate Status Transition<br/>(PENDING → APPROVED)
    
    alt Valid Transition
        Validator-->>Service: Valid
        Service->>Database: Update Loan Status to APPROVED
        Service->>Database: Set approved_by, status_changed_at
        Database-->>Service: Success
        Service->>Audit: Log Approval Action
        Service-->>API: Updated Loan
        API-->>User: 200 OK
    else Invalid Transition
        Validator-->>Service: LoanStatusTransitionError
        Service-->>API: Error
        API-->>User: 422 Validation Error
    end
```

## 7. User Management Flow

```mermaid
flowchart TD
    Start([Request]) --> CheckAuth{Authenticated?}
    CheckAuth -->|No| AuthError[401 Unauthorized]
    CheckAuth -->|Yes| CheckSuperAdmin{Is Super Admin?}
    
    CheckSuperAdmin -->|No| PermissionError[403 Forbidden]
    CheckSuperAdmin -->|Yes| Action{Action Type}
    
    Action -->|Create User| CreateUser[Create User Flow]
    Action -->|List Users| ListUsers[List Users Flow]
    Action -->|Get User| GetUser[Get User by ID Flow]
    Action -->|Update User| UpdateUser[Update User Flow]
    Action -->|Delete User| DeleteUser[Delete User Flow]
    Action -->|Activate/Deactivate| ActivateUser[Activate/Deactivate Flow]
    
    CreateUser --> ValidateUserData[Validate User Data]
    ValidateUserData -->|Invalid| ValidationError[422 Validation Error]
    ValidateUserData -->|Valid| CheckUnique{Check Username<br/>& Email Uniqueness}
    CheckUnique -->|Duplicate| DuplicateError[422: Username/Email Exists]
    CheckUnique -->|Unique| HashPassword[Hash Password]
    HashPassword --> CreateInDB[Create User in Database]
    CreateInDB --> AuditLog1[Log to Audit]
    AuditLog1 --> Success1[201 Created]
    
    ListUsers --> QueryUsers[Query Users with Filters]
    QueryUsers --> CheckEmpty{Data Empty?}
    CheckEmpty -->|Yes| NotFound[404 Not Found]
    CheckEmpty -->|No| Success2[200 OK with Data]
    
    GetUser --> GetUserByID[Get User by ID]
    GetUserByID -->|Not Found| NotFound
    GetUserByID -->|Found| CheckOwner{Is Owner or<br/>Super Admin?}
    CheckOwner -->|No| PermissionError
    CheckOwner -->|Yes| Success3[200 OK]
    
    UpdateUser --> GetUserByID2[Get User by ID]
    GetUserByID2 -->|Not Found| NotFound
    GetUserByID2 -->|Found| CheckUpdatePermission{Can Update?<br/>(Owner or Admin)}
    CheckUpdatePermission -->|No| PermissionError
    CheckUpdatePermission -->|Yes| ValidateUpdate[Validate Update Data]
    ValidateUpdate --> UpdateInDB[Update User in Database]
    UpdateInDB --> AuditLog2[Log to Audit]
    AuditLog2 --> Success4[200 OK]
    
    DeleteUser --> GetUserByID3[Get User by ID]
    GetUserByID3 -->|Not Found| NotFound
    GetUserByID3 -->|Found| DeleteFromDB[Delete User from Database]
    DeleteFromDB --> AuditLog3[Log to Audit]
    AuditLog3 --> Success5[200 OK]
    
    ActivateUser --> GetUserByID4[Get User by ID]
    GetUserByID4 -->|Not Found| NotFound
    GetUserByID4 -->|Found| ToggleStatus[Toggle is_active Status]
    ToggleStatus --> AuditLog4[Log to Audit]
    AuditLog4 --> Success6[200 OK]
    
    AuthError --> End([End])
    PermissionError --> End
    ValidationError --> End
    DuplicateError --> End
    NotFound --> End
    Success1 --> End
    Success2 --> End
    Success3 --> End
    Success4 --> End
    Success5 --> End
    Success6 --> End
    
    style CheckAuth fill:#ffeb3b
    style CheckSuperAdmin fill:#ff9800
    style CheckOwner fill:#ff9800
    style CheckUpdatePermission fill:#ff9800
    style Success1 fill:#4caf50
    style Success2 fill:#4caf50
    style Success3 fill:#4caf50
    style Success4 fill:#4caf50
    style Success5 fill:#4caf50
    style Success6 fill:#4caf50
    style AuthError fill:#f44336
    style PermissionError fill:#f44336
    style ValidationError fill:#f44336
    style DuplicateError fill:#f44336
    style NotFound fill:#f44336
```

## 8. Complete Application Flow Overview

```mermaid
flowchart TB
    subgraph "Authentication Layer"
        Login[Login Endpoint]
        Refresh[Refresh Token]
        Logout[Logout]
    end
    
    subgraph "Authorization Layer"
        JWTValidation[JWT Token Validation]
        PermissionCheck[Permission Check]
        RoleCheck[Role Check]
    end
    
    subgraph "Business Logic Layer"
        AssetMgmt[Asset Management]
        LoanMgmt[Loan Management]
        UserMgmt[User Management]
        AuditLog[Audit Logging]
    end
    
    subgraph "Data Layer"
        Database[(PostgreSQL Database)]
    end
    
    Login --> JWTValidation
    JWTValidation --> PermissionCheck
    PermissionCheck --> RoleCheck
    
    RoleCheck --> AssetMgmt
    RoleCheck --> LoanMgmt
    RoleCheck --> UserMgmt
    
    AssetMgmt --> Database
    LoanMgmt --> Database
    UserMgmt --> Database
    
    AssetMgmt --> AuditLog
    LoanMgmt --> AuditLog
    UserMgmt --> AuditLog
    
    AuditLog --> Database
    
    style Login fill:#2196f3
    style JWTValidation fill:#ff9800
    style PermissionCheck fill:#ff9800
    style AssetMgmt fill:#4caf50
    style LoanMgmt fill:#4caf50
    style UserMgmt fill:#4caf50
    style AuditLog fill:#9c27b0
    style Database fill:#607d8b
```

## 9. Error Handling Flow

```mermaid
flowchart TD
    Start([Request]) --> Process[Process Request]
    Process --> Error{Error Occurs?}
    
    Error -->|No| Success[200 OK Response]
    Error -->|Yes| ErrorType{Error Type}
    
    ErrorType -->|BaseAPIException| CustomError[Return Custom Error Response]
    ErrorType -->|RequestValidationError| ValidationError[Return Validation Error Response]
    ErrorType -->|Exception| GeneralError[Return Generic Error Response]
    
    CustomError --> LogError[Log Error to Logger]
    ValidationError --> LogError
    GeneralError --> LogError
    
    LogError --> CheckErrorType{Check Error Type}
    
    CheckErrorType -->|Database Error| UserFriendly1[Database error occurred.<br/>Please contact administrator.]
    CheckErrorType -->|Connection Error| UserFriendly2[Connection error.<br/>Please try again later.]
    CheckErrorType -->|Validation Error| UserFriendly3[Invalid data provided.<br/>Please check your input.]
    CheckErrorType -->|Permission Error| UserFriendly4[You don't have permission<br/>to perform this action.]
    CheckErrorType -->|Not Found| UserFriendly5[The requested resource<br/>was not found.]
    CheckErrorType -->|Other| UserFriendly6[An error occurred.<br/>Please try again later.]
    
    UserFriendly1 --> ErrorResponse[Return Error Response<br/>with User-Friendly Message]
    UserFriendly2 --> ErrorResponse
    UserFriendly3 --> ErrorResponse
    UserFriendly4 --> ErrorResponse
    UserFriendly5 --> ErrorResponse
    UserFriendly6 --> ErrorResponse
    
    Success --> End([End])
    ErrorResponse --> End
    
    style Error fill:#ffeb3b
    style ErrorType fill:#ff9800
    style Success fill:#4caf50
    style ErrorResponse fill:#f44336
    style LogError fill:#9c27b0
```

## 10. Permission Matrix

```mermaid
graph LR
    subgraph "Super Admin Permissions"
        SA1[MANAGE_USERS]
        SA2[VIEW_USERS]
        SA3[MANAGE_ROLES]
        SA4[VIEW_ROLES]
        SA5[MANAGE_ASSETS]
        SA6[VIEW_ASSETS]
        SA7[MANAGE_CATEGORIES]
        SA8[VIEW_CATEGORIES]
        SA9[MANAGE_LOANS]
        SA10[VIEW_OWN_LOANS]
        SA11[CREATE_LOAN]
        SA12[RETURN_LOAN]
        SA13[VIEW_AUDIT_LOGS]
    end
    
    subgraph "User Permissions"
        U1[VIEW_ASSETS]
        U2[VIEW_CATEGORIES]
        U3[VIEW_OWN_LOANS]
        U4[CREATE_LOAN]
        U5[RETURN_LOAN]
    end
    
    style SA1 fill:#4caf50
    style SA2 fill:#4caf50
    style SA3 fill:#4caf50
    style SA4 fill:#4caf50
    style SA5 fill:#4caf50
    style SA6 fill:#4caf50
    style SA7 fill:#4caf50
    style SA8 fill:#4caf50
    style SA9 fill:#4caf50
    style SA10 fill:#4caf50
    style SA11 fill:#4caf50
    style SA12 fill:#4caf50
    style SA13 fill:#4caf50
    
    style U1 fill:#2196f3
    style U2 fill:#2196f3
    style U3 fill:#2196f3
    style U4 fill:#2196f3
    style U5 fill:#2196f3
```

## Catatan

1. **Authentication**: Semua request memerlukan JWT token (kecuali login)
2. **Authorization**: Setiap endpoint memeriksa permission sesuai role
3. **Audit Logging**: Semua operasi penting dicatat di audit log
4. **Error Handling**: Semua error ditampilkan dengan pesan user-friendly
5. **Status Transition**: Loan status mengikuti state machine yang valid
6. **Data Validation**: Semua input data divalidasi sebelum diproses

## Tools untuk View Diagram

Diagram di atas menggunakan format Mermaid yang dapat dirender di:
- GitHub/GitLab (otomatis)
- VS Code dengan extension Mermaid Preview
- Online: https://mermaid.live/
- Dokumentasi: https://mermaid.js.org/

