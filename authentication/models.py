from django.db import models
from django.contrib.auth.models import User
from user.models import Category
# Create your models here.
class UserCategory(models.Model):
    category_name = models.CharField(max_length=15)
    def __str__(self):
        return self.category_name

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    category = models.ForeignKey(UserCategory,on_delete=models.CASCADE)
    bio = models.TextField(default="enter bio")
    cover_photo = models.ImageField(upload_to="cover_photo/",default="test.jpg")
    profile_photo = models.ImageField(upload_to="profile_photo/",default="test.jpg")
    name_of_school = models.CharField(max_length=50,default="")
    level_of_education = models.CharField(max_length=50,default="") 
    flags = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.user} profile"

  


class Prefrence(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, verbose_name=("categories"))

    def __str__(self):
        return f"{self.user} prefrences"



# class Connection(models.Model):
#     user = models.ManyToManyField(User,symmetrical=False)    

#     def __str__(self):
#         return self.name


from django.core.exceptions import ValidationError
from django.db.models import Q


class ConnectionManager(models.Manager):
    """Custom manager for Connection model with useful query methods"""
    
    def get_user_connections(self, user):
        """Get all accepted connections for a user (both sent and received)"""
        return self.filter(
            Q(sender=user) | Q(receiver=user),
            status=Connection.Status.ACCEPTED
        )
    
    def get_pending_sent(self, user):
        """Get all pending connection requests sent by user"""
        return self.filter(
            sender=user,
            status=Connection.Status.PENDING
        )
    
    def get_pending_received(self, user):
        """Get all pending connection requests received by user"""
        return self.filter(
            receiver=user,
            status=Connection.Status.PENDING
        )
    
    def are_connected(self, user1, user2):
        """Check if two users are connected"""
        return self.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1),
            status=Connection.Status.ACCEPTED
        ).exists()
    
    def get_connection_status(self, user1, user2):
        """Get the connection status between two users"""
        connection = self.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)
        ).first()
        return connection.status if connection else None
    
    def get_mutual_connections(self, user1, user2):
        """Get mutual connections between two users"""
        user1_connections = self.get_user_connections(user1).values_list('sender', 'receiver')
        user2_connections = self.get_user_connections(user2).values_list('sender', 'receiver')
        
        # Extract all connected user IDs for both users
        user1_connected_ids = set()
        for sender, receiver in user1_connections:
            user1_connected_ids.add(sender if sender != user1.id else receiver)
        
        user2_connected_ids = set()
        for sender, receiver in user2_connections:
            user2_connected_ids.add(sender if sender != user2.id else receiver)
        
        # Find intersection
        mutual_ids = user1_connected_ids.intersection(user2_connected_ids)
        return User.objects.filter(id__in=mutual_ids)


class Connection(models.Model):
    """
    Model representing connections between users on LinkedIn.
    Handles pending, accepted, and rejected connection states.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_connections',
        help_text='User who initiated the connection request'
    )
    
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_connections',
        help_text='User who received the connection request'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text='Current status of the connection'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the connection request was created'
    )

    # updated_at = models.DateTimeField(
    #     auto_now=True,
    #     help_text='When the connection was last updated'
    # )
    
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the connection was accepted'
    )
    
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the connection was rejected'
    )
    
    # Custom manager
    objects = ConnectionManager()
    
    class Meta:
        db_table = 'connections'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['status', 'created_at']),
        ]
        # Ensure we don't have duplicate active requests between same users
        constraints = [
            models.CheckConstraint(
                check=~Q(sender=models.F('receiver')),
                name='prevent_self_connection'
            )
        ]
    
    def clean(self):
        """Validate the connection before saving"""
        if self.sender == self.receiver:
            raise ValidationError("Users cannot connect with themselves")
        
        # Check for existing pending connection in either direction
        if self.pk is None:  # Only for new connections
            existing = Connection.objects.filter(
                Q(sender=self.sender, receiver=self.receiver) |
                Q(sender=self.receiver, receiver=self.sender),
                status=Connection.Status.PENDING
            ).exists()
            
            if existing:
                raise ValidationError(
                    "A pending connection request already exists between these users"
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def accept(self):
        """Accept the connection request"""
        from django.utils import timezone
        
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending connections can be accepted")
        
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save()
    
    def reject(self):
        """Reject the connection request"""
        from django.utils import timezone
        
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending connections can be rejected")
        
        self.status = self.Status.REJECTED
        self.rejected_at = timezone.now()
        self.save()
    
    def get_other_user(self, user):
        """Get the other user in the connection"""
        if user == self.sender:
            return self.receiver
        elif user == self.receiver:
            return self.sender
        else:
            raise ValueError("User is not part of this connection")
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"
    
    def __repr__(self):
        return (
            f"<Connection: {self.sender.username} -> {self.receiver.username} "
            f"({self.status})>"
        )