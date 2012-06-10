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

        <div class="block block-task block-task-student block-task-owned block-task-completed level-medium">
            <div class="cog"></div>
            <div class="block-title clearfix">
                <div class="block-task-title">
                    <span class="title">Write documentation for export function</span>
                    <span class="project">Drupal Foundation</span>
                </div>
                <div class="block-task-action">
                    <span class="block-task-action-title">This is your current task!</span>
                    <form action="#" method="post">
                    <input type="submit" class="task-btn task-btn-unclaim" value="Unclaim task" />
                    </form>
                </div>
            </div>
        	<div class="block-task-difficulty">
        	    <span class="difficulty">Difficulty: <span class="emph">Medium</span></span>
        	    <span class="status">Status: <span class="emph">In progress</span></span>
        	    <span class="remaining">Time left: <span class="emph">5 hrs 6 min</span></span>
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
        	<div class="block-task-uploaded-code">
        	    <span class="block-task-uploaded-code-title">Uploaded code</span>
        	    <div class="block-task-uploaded-code-content">
        	        <span class="block-task-uploaded-code-note">Upload your final work file or paste in its URL, then click Submit.</span>
        	        <form action="#" method="post" class="form-upload-code form-student-upload-code clearfix">
        	            <div class="form-row form-row-student-work-upload-file">
        	                <input type="file" name="datafile">
        	            </div>
        	            <div class="form-row form-row-student-work-url">
        	                <input name="final-work-url" value="http://" type="text">
        	            </div>
        	            <div class="form-row form-row-buttons">
        	            	<input value="Submit" class="button" type="submit">
        	            </div>
        	        </form>
        	    </div>
        	</div>
        	<!-- end .block-task-uploaded-code -->
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
        	    <div class="single-comment">
        	        <span class="single-comment-title">This is a great task idea.</span>
        	        <span class="single-comment-meta">by <a href="javascript:void(0)">Eric Schmidt</a> July 28 2011 10:57 GMT</span>
        	        <p>Praesent porta nunc diam, sed ullamcorper turpis. Praesent dignissim eleifend sapien pellentesque fermentum. Etiam feugiat lacinia lorem, semper varius ligula ornare eget. Nunc at risus ante. Maecenas vehicula lacinia vestibulum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; aliquam erat volutpat!</p>
        	        <input type="submit" class="task-btn task-btn-comment-reply" value="Reply" />
        	        <div class="single-comment-reply">
        	            <span class="single-comment-reply-title">Reply</span>
        	            <form action="#" method="post" class="form-comment-reply clearfix">
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
        	        <!--end .single-comment-reply-->    
        	    </div>
        	    <!-- end .single-comment -->
        	</div>
        	<!-- end .block-comments -->
        </div>
        <!-- end .block.block-task.block-task-mentor -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>