<?php include '../includes/header.php'?>

    <div class="grid_3 side">
        <div class="block block-main-nav">
            <ul class="menu">
                <li><a href="javascript:void(0)">My Dashboard</a></li>
                <li><a href="javascript:void(0)">About Us</a></li>
                <li><a href="javascript:void(0)">Get Started</a></li>
                <li><a href="javascript:void(0)">Participating Organizations</a></li>
                <li><a href="javascript:void(0)">Blog</a></li>
            </ul>
        </div>
        <!-- end .block.block-main-nav -->
        
        <div class="block block-status block-status-sm">
            <div class="block-status-user">
                You are logged in as: <a href="javascript:void(0)">eric_schmidt@gmail.com</a> <a href="javascript:void(0)">(change)</a>
            </div>
            <div class="block-status-action block-status-action-single clearfix">
                <a href="javascript:void(0)" class="block-status-action-dashboard"><span>My Dashboard</span></a>
            </div>
        </div>
        <!-- end .block.block-status.block-status-sm -->
    </div>
    <!-- end .grid_3.side -->
    <div class="grid_9 main">

        <div class="block block-task block-task-student block-task-open level-medium">
            <div class="cog"></div>
            <div class="block-title clearfix">
                <div class="block-task-title">
                    <span class="title">Write documentation for export function</span>
                    <span class="project">Drupal Foundation</span>
                </div>
                <div class="block-task-action">
                	<form action="#" method="post">
                	<input type="submit" class="btn btn-claim-task" value="Claim this task!" />
                	<input type="submit" class="task-btn task-btn-subscribe-updates" value="Subscribe to updates" />
                	</form>
                </div>
            </div>
        	<div class="block-task-difficulty">
        	    <span class="difficulty">Difficulty: <span class="emph">Medium</span></span>
        	    <span class="remaining">Time to complete: <span class="emph">12 hours</span></span>
        	</div>
        	<div class="block-content clearfix">
        	    <div class="block-task-description">
            	    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis porttitor purus massa. Aliquam erat volutpat. Maecenas vitae neque ipsum. Morbi scelerisque varius augue ac euismod. Pellentesque euismod augue a justo mollis eu tempor nunc ultricies. Fusce pharetra convallis dignissim...</p>
            	    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis porttitor purus massa. Aliquam erat volutpat. Maecenas vitae neque ipsum. Morbi scelerisque varius augue ac euismod. Pellentesque euismod augue a justo mollis eu tempor nunc ultricies. Fusce pharetra convallis dignissim...</p>
            	    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis porttitor purus massa. Aliquam erat volutpat. Maecenas vitae neque ipsum. Morbi scelerisque varius augue ac euismod. Pellentesque euismod augue a justo mollis eu tempor nunc ultricies. Fusce pharetra convallis dignissim...</p>
            	    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis porttitor purus massa. Aliquam erat volutpat. Maecenas vitae neque ipsum. Morbi scelerisque varius augue ac euismod. Pellentesque euismod augue a justo mollis eu tempor nunc ultricies. Fusce pharetra convallis dignissim...</p>
        	    </div>
        	    <!-- end .block-task-description -->
        	</div>
        	<div class="block-comments clearfix">
        	    <span class="block-comments-title">Comments</span>
        	    <input type="submit" class="task-btn task-btn-comment-new" value="Post new comment" />
        	    <div class="block-comments-post-new">
        	        <span class="block-comments-post-new-title">Post new comment</span>
        	        <form action="#" method="post" class="form-comment-post-new clearfix">
        	            <div class="form-row">
        	                <label for="comment-reply-title" class="form-label">Title</label>
        	                <input name="comment-reply-title" value="" type="text">
        	            </div>
        	            <div class="form-row">
        	                <label for="comment-reply-body" class="form-label">Body</label>
        	                <textarea id="comment-reply-body" name="comment-reply-body"></textarea>
        	            </div>
        	            <div class="form-row form-row-buttons">
        	            	<input value="Submit" class="button" type="submit">
        	            </div>
        	        </form>
        	    </div>
        	    <!--end .block-comments-post-new-->  
        	</div>
        	<!-- end .block-comments -->
        </div>
        <!-- end .block.block-task.block-task-mentor -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>