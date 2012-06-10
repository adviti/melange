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
                You are logged in as: <a href="javascript:void(0)">maya.jones@gmail.com</a> <a href="javascript:void(0)">(change)</a>
            </div>
            <div class="block-status-action block-status-action-single clearfix">
                <a href="javascript:void(0)" class="block-status-action-dashboard"><span>My Dashboard</span></a>
            </div>
        </div>
        <!-- end .block.block-status.block-status-sm -->
    </div>
    <!-- end .grid_3.side -->
    <div class="grid_9 main">

        <div class="block block-task block-task-mentor level-medium">
            <div class="cog"></div>
            <div class="block-title clearfix">
                <div class="block-task-title">
                    <span class="title">Write documentation for export function</span>
                    <span class="project">Drupal Foundation</span>
                </div>
                <div class="block-task-action">
                    <span class="block-task-action-title">You are mentor for this task.</span>
                    <form action="#" method="post">
                    <input type="submit" class="task-btn task-btn-close" value="Mark task as closed" />
                    <input type="submit" class="task-btn task-btn-unassign" value="Unassign task" />
                    <input type="submit" class="task-btn task-btn-edit" value="Edit task" />
                    <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                    </form>
                </div>
            </div>
        	<div class="block-task-difficulty">
        	    <span class="difficulty">Difficulty: <span class="emph">Medium</span></span>
        	    <span class="status">Status: <span class="emph">In progress</span></span>
        	    <span class="remaining">Time left: <span class="emph">5 hrs 6 min</span></span>
        	    <span class="mentor">Mentor: <span class="emph">Carol Smith</span></span>
        	</div>
        	<div class="block-content clearfix">
        	    <div class="block-task-countdown">
        	        <div class="stopwatch percent-33 clearfix">
        	            <div class="stopwatch-watch"></div>
        	            <div class="stopwatch-remaining clearfix">
        	                <div class="stopwatch-time">
        	                    <div class="stopwatch-time-c">
        	                        <div class="time time-first">
        	                            <span class="number">35</span><span class="cap">days</span>
        	                        </div>
        	                        <div class="time">
        	                            <span class="number">17</span><span class="cap">hours</span>
        	                        </div>
        	                    </div>
        	                </div>
        	                <span class="remain">Remaining</span>
        	                <span class="timestamp">as of 7/23 @3:30GMT</span>
        	            </div>
        	            <input type="submit" class="task-btn task-btn-extended-deadline" value="Extend deadline" />
        	            <div id="deadline-extend">
        	            	<div id="deadline-extend-close">x</div>
        	            	<div class="deadline-extend-top"></div>
        	            	<div class="deadline-extend-content">
	        	            	<span class="plus">+ </span>
		        	            <form action="#" method="post" class="clearfix">
		        	            	<fieldset id="fieldset-error">
		        	            		<div class="form-row">
		        	            		    <input value="" type="text"> <span class="time">hours</span>
		        	            		</div>
		        	            		<input value="Confirm" class="task-btn task-btn-confirm-extended-deadline" type="submit">
		        	            	</fieldset>
		        	            </form>
	        	            </div>
        	            </div>
        	        </div>
        	        <!-- end .stockwatch -->
        	    </div>
        	    <!-- end .block-task-countdown -->
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
        	        <span class="block-task-uploaded-code-status">No code has been uploaded yet.</span>
        	        <form action="#" method="post" class="form-upload-code clearfix">
            	        <div class="form-row form-row-file-upload">
            	            <input type="file" name="datafile">
            	        </div>
            	        <div class="form-row form-row-buttons">
            	        	<input value="Submit" class="button" type="submit">
            	        </div>
        	        </form>
        	    </div>
        	</div>
        	<!-- end .block-task-uploaded-code -->
        </div>
        <!-- end .block.block-task.block-task-mentor -->
        <div class="block block-tabs block-user-tabs block-secondary-tabs">
          <ul>
            <li><a href="#comments">Comments</a></li>
            <li><a href="#changelog">Change Log</a></li>
          </ul>
          <div id="comments" class="task-group">
            <div class="block-comments clearfix">
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
          <div id="changelog" class="task-group">
            <div class="block-changelog clearfix">
              <div class="single-changelog changelog-student">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-eric-schmidt.png"/>
                </div>
                <div class="single-changelog-heading">
                  Student <a href="javascript:void(0)">Eric Schmidt</a> <span class="single-changelog-action">requested</span> to <span class="single-changelog-action">claim</span> this task. 
                </div>
                <div class="single-changelog-date">
                  July 28 2011 10:57 UTC
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-student">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-eric-schmidt.png"/>
                </div>
                <div class="single-changelog-heading">
                  Student <a href="javascript:void(0)">Eric Schmidt</a> <span class="single-changelog-action">commented</span> on this task. 
                </div>
                <div class="single-changelog-date">
                  July 28 2011 10:57 UTC
                </div>
                <div class="single-changelog-comment">
                  I have worked with wordpress before and have wrote plugins/edited existing plugins. I have read over some of the core classes, and am familiar with how they work. I have been doing PHP for 4+ years, and believe I can write this patch.
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-student">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-travis-ralston.png"/>
                </div>
                <div class="single-changelog-heading">
                  Student <a href="javascript:void(0)">Travis Ralston</a> <span class="single-changelog-action">requested</span> to <span class="single-changelog-action">claim</span> this task. 
                </div>
                <div class="single-changelog-date">
                  July 28 2011 11:33 UTC
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-student">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-travis-ralston.png"/>
                </div>
                <div class="single-changelog-heading">
                  Student <a href="javascript:void(0)">Travis Ralston</a> <span class="single-changelog-action">commented</span> on this task. 
                </div>
                <div class="single-changelog-date">
                  July 28 2011 11:33 UTC
                </div>
                <div class="single-changelog-comment">
                  I use WordPress a lot, I've used it for my own personal blog, set some up for others, and I am working on trying to create a plugin for it. I have extensive knowledge in PHP, and other languages.
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-student">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-eric-schmidt.png"/>
                </div>
                <div class="single-changelog-heading">
                  Student <a href="javascript:void(0)">Eric Schmidt</a> <span class="single-changelog-action">withdrew</span> his <span class="single-changelog-action">claim request</span>. 
                </div>
                <div class="single-changelog-date">
                  July 29 2011 12:41 UTC
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-mentor changelog-self">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-maya-smith.png"/>
                </div>
                <div class="single-changelog-heading">
                  Mentor <a href="javascript:void(0)">Maya Smith</a> <span class="single-changelog-action">assigned</span> <a href="javascript:void(0)">Travis Ralston</a> to this task. 
                </div>
                <div class="single-changelog-date">
                  July 30 2011 2:20 UTC
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-mentor changelog-self">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-maya-smith.png"/>
                </div>
                <div class="single-changelog-heading">
                  Mentor <a href="javascript:void(0)">Maya Smith</a> <span class="single-changelog-action">extended</span> the <span class="single-changelog-action">task deadline</span> to July 31 2011 7:00 UTC.
                </div>
                <div class="single-changelog-date">
                  July 30 2011 2:20 UTC
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-student">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-travis-ralston.png"/>
                </div>
                <div class="single-changelog-heading">
                  Student <a href="javascript:void(0)">Travis Ralston</a> uploaded work. (<a href="javascript:void(0)">Download here</a>)
                </div>
                <div class="single-changelog-date">
                  July 31 2011 6:27 UTC
                </div>
              </div>
              <!-- end .single-changelog -->
              <div class="single-changelog changelog-mentor changelog-self">
                <div class="single-changelog-avatar">
                  <img src="../images/avatar-30-maya-smith.png"/>
                </div>
                <div class="single-changelog-heading">
                  Mentor <a href="javascript:void(0)">Maya Smith</a> <span class="single-changelog-action">commented</span> on this task. 
                </div>
                <div class="single-changelog-date">
                  July 31 2011 10:20 UTC
                </div>
                <div class="single-changelog-comment">
                  Great work, Travis!
                </div>
              </div>
              <!-- end .single-changelog -->
            </div>
            <!-- end .block-changelog -->
          </div>
        </div>
        <!-- end .block.block-secondary-tabs -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>
